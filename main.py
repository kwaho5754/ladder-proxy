from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 변환 함수
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 대칭 변환 함수 (3분의 2 기준)
def transform_to_symmetry(pattern):
    if len(pattern) != 4:
        return None
    direction = pattern[0]
    line = pattern[1]
    line_mirror = "4" if direction == "좌" else "3"
    oe_mirror = "짝" if line == "3" else "홀"
    return line_mirror + oe_mirror

# 정방향 예측 함수 (앞 3분의2 블럭 기준)
def predict_by_partial_block(pattern_list, block_size):
    if len(pattern_list) < block_size:
        return "없음"
    block = pattern_list[:block_size]
    partial = block[:block_size - 1]
    transformed = [transform_to_symmetry(p) for p in partial if transform_to_symmetry(p)]

    for i in range(block_size, len(pattern_list)):
        candidate_block = pattern_list[i:i + block_size]
        if len(candidate_block) < block_size:
            continue
        candidate_partial = candidate_block[:block_size - 1]
        transformed_candidate = [transform_to_symmetry(p) for p in candidate_partial if transform_to_symmetry(p)]
        if transformed == transformed_candidate:
            return pattern_list[i]
    return "없음"

# 역방향 예측 함수 (뒤 3분의2 블럭 기준)
def predict_by_reverse_flow(pattern_list, block_size):
    if len(pattern_list) < block_size:
        return "없음"
    block = pattern_list[:block_size][::-1]  # 최근에서 과거로 거꾸로 블럭 조립
    partial = block[:block_size - 1]         # 앞 방향으로 쪼갬 (최근 줄부터 기준)
    transformed = [transform_to_symmetry(p) for p in partial if transform_to_symmetry(p)]

    for i in range(block_size, len(pattern_list)):
        candidate = pattern_list[i:i + block_size][::-1]  # 과거 블럭도 뒤에서부터 거꾸로 구성
        candidate_partial = candidate[:block_size - 1]
        transformed_candidate = [transform_to_symmetry(p) for p in candidate_partial if transform_to_symmetry(p)]

        if transformed == transformed_candidate:
            return pattern_list[i]  # 블럭의 상단값 (가장 최근줄)
    return "없음"

# 예측 회차 계산
def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()
        if not data or len(data) < 10:
            raise ValueError("데이터 부족")

        predict_round = get_predict_round(data)
        pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]

        front_predictions = []
        back_predictions = []

        for size in range(2, 7):
            front_predictions.append(predict_by_partial_block(pattern_list, size))
            back_predictions.append(predict_by_reverse_flow(pattern_list, size))

        return jsonify({
            "predict_round": predict_round,
            "front_predictions": front_predictions,
            "back_predictions": back_predictions
        })
    except Exception as e:
        return jsonify({
            "predict_round": -1,
            "front_predictions": ["에러"] * 5,
            "back_predictions": ["에러"] * 5
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
