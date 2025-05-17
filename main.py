from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴명 변환 (LEFT, 3, ODD → 좌삼홀)
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 3분의2 대칭 변환 (좌삼짝 → 우사홀)
def transform_to_symmetry(pattern):
    if len(pattern) != 4:
        return None
    direction = pattern[0]
    line = pattern[1]
    line_mirror = "4" if line == "3" else "3"
    direction_mirror = "우" if direction == "좌" else "좌"
    oe_mirror = "짝" if line == "3" else "홀"
    return f"{direction_mirror}{line_mirror}{oe_mirror}"

# 블럭 기반 예측 함수 (정방향 or 역방향)
def predict_block_patterns(pattern_list, reverse=False):
    predictions = []
    for block_size in range(2, 7):  # 2~6줄 블럭
        for i in range(len(pattern_list) - block_size):
            current_block = pattern_list[i:i + block_size]
            if reverse:
                # 뒤 기준: 블럭 대칭 후 현재와 비교, 예측값은 '앞쪽(상단)'
                transformed = [transform_to_symmetry(p) for p in current_block]
                match_block = transformed[::-1]
                for j in range(len(pattern_list) - block_size):
                    if pattern_list[j:j + block_size] == match_block:
                        predictions.append(pattern_list[j - 1] if j > 0 else None)
            else:
                # 앞 기준: 블럭 대칭 후 현재와 비교, 예측값은 '뒤쪽(상단)'
                transformed = [transform_to_symmetry(p) for p in current_block]
                match_block = transformed
                for j in range(len(pattern_list) - block_size):
                    if pattern_list[j:j + block_size] == match_block:
                        if j + block_size < len(pattern_list):
                            predictions.append(pattern_list[j + block_size])
    predictions = [p for p in predictions if p]
    counter = Counter(predictions)
    return [item[0] for item in counter.most_common(5)]

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()
        pattern_list = [
            convert_pattern_name(item["start"], item["line"], item["odd_even"])
            for item in data
        ][::-1]  # 최신값이 마지막에 있도록 뒤집음

        top1_5 = predict_block_patterns(pattern_list, reverse=False)
        top6_10 = predict_block_patterns(pattern_list, reverse=True)

        return jsonify({
            "round": f"{len(pattern_list)}회차",
            "top1_5": top1_5,
            "top6_10": top6_10
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)