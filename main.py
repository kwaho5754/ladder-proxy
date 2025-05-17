from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 변환: start, line, odd_even → 예: 좌3홀
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 대칭 변환: 좌삼홀 ↔ 우사짝
def transform_to_symmetry(pattern):
    if len(pattern) != 4:
        return None
    direction_map = {"좌": "우", "우": "좌"}
    line_map = {"삼": "사", "사": "삼"}
    odd_even_map = {"홀": "짝", "짝": "홀"}
    return (
        direction_map.get(pattern[0], "") +
        line_map.get(pattern[1], "") +
        odd_even_map.get(pattern[2:], "")
    )

# 블럭 예측 함수
def predict_block_patterns(pattern_list, reverse=False):
    predictions = []
    for block_size in range(2, 7):  # 블럭 크기: 2~6
        for i in range(len(pattern_list) - block_size):
            block = pattern_list[i:i + block_size]
            two_thirds_len = max(1, block_size * 2 // 3)
            base = block[:two_thirds_len]
            transformed = [transform_to_symmetry(p) for p in base]

            # 찾을 기준 패턴: 정방향이면 그대로, 역방향이면 반전
            search_pattern = transformed if not reverse else transformed[::-1]

            for j in range(len(pattern_list) - block_size):
                candidate = pattern_list[j:j + two_thirds_len]
                if candidate == search_pattern:
                    if j > 0:
                        predictions.append(pattern_list[j - 1])  # 항상 상단 값
    return [p for p in predictions if p]

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()
        pattern_list = [
            convert_pattern_name(item["start"], item["line"], item["odd_even"])
            for item in data
        ][::-1]  # 최신값이 뒤로 오도록

        # 앞/뒤 기준 예측값 추출
        front = predict_block_patterns(pattern_list, reverse=False)
        back = predict_block_patterns(pattern_list, reverse=True)

        # 빈도 상위 5개씩 추출
        front_top5 = [x[0] for x in Counter(front).most_common(5)]
        back_top5 = [x[0] for x in Counter(back).most_common(5)]

        return jsonify({
            "predict_round": len(pattern_list),
            "front_predictions": front_top5,
            "back_predictions": back_top5
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
