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
    oe = pattern[2:]
    # 좌/우를 3/4로 대응하고 홀/짝 유지
    line_mirror = "4" if direction == "좌" else "3"
    oe_mirror = "짝" if line == "3" else "홀"  # 줄수 기준 반전 (예외적 로직)
    return line_mirror + oe_mirror

# 블럭 기반 예측 (상단 블럭 사용)
def predict_top_by_block(pattern_list, block_size):
    if len(pattern_list) < block_size:
        return "없음"
    recent_block = pattern_list[:block_size]
    recent_partial = recent_block[:block_size - 1]  # 3분의2
    transformed = [transform_to_symmetry(p) for p in recent_partial if transform_to_symmetry(p)]

    for i in range(block_size, len(pattern_list)):
        candidate_block = pattern_list[i:i + block_size]
        if len(candidate_block) < block_size:
            continue
        candidate_partial = candidate_block[:block_size - 1]
        transformed_candidate = [transform_to_symmetry(p) for p in candidate_partial if transform_to_symmetry(p)]
        if transformed == transformed_candidate:
            upper_index = i - 1
            if upper_index >= 0:
                return pattern_list[upper_index]
    return "없음"

# 균형 조합 기반은 블럭 2줄 기준 사용
def predict_combo_by_2block(pattern_list):
    return predict_top_by_block(pattern_list, block_size=2)

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
            return "데이터 부족"

        predict_round = get_predict_round(data)
        pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]

        top1 = predict_top_by_block(pattern_list, 3)
        top2 = predict_top_by_block(pattern_list, 4)
        top3 = predict_top_by_block(pattern_list, 5)
        combo = predict_combo_by_2block(pattern_list)

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": [top1, top2, top3],
            "combo_suggestion": combo
        })
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
