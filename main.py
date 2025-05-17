from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 변환: 예) LEFT, 3, ODD → 좌삼홀
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 대칭 변환: 좌삼홀 ↔ 우사짝
def transform_to_symmetry(pattern):
    if len(pattern) != 4:
        return None
    direction = pattern[0]
    line = pattern[1]
    odd_even = pattern[2:]

    direction_map = {"좌": "우", "우": "좌"}
    line_map = {"3": "4", "4": "3"}
    odd_even_map = {"홀": "짝", "짝": "홀"}

    return (
        direction_map.get(direction, "") +
        line_map.get(line, "") +
        odd_even_map.get(odd_even, "")
    )

# 블럭 기반 예측 함수 (정방향 or 역방향)
def predict_block_patterns(pattern_list, reverse=False):
    predictions = []

    for block_size in range(2, 7):  # 블럭 사이즈 2~6줄
        for i in range(len(pattern_list) - block_size):
            block = pattern_list[i:i + block_size]
            two_thirds_len = max(1, block_size * 2 // 3)

            # 블럭의 앞 3분의 2만 사용해서 대칭 변환
            base = block[:two_thirds_len]
            transformed = [transform_to_symmetry(p) for p in base]

            if None in transformed:
                continue

            search_pattern = transformed if not reverse else transformed[::-1]

            for j in range(len(pattern_list) - two_thirds_len):
                candidate = pattern_list[j:j + two_thirds_len]
                if candidate == search_pattern:
                    if j > 0:
                        predictions.append(pattern_list[j - 1])  # 항상 상단값

    return [p for p in predictions if p]

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()

        pattern_list = [
            convert_pattern_name(item["start_point"], item["line_count"], item["odd_even"])
            for item in data
        ][::-1]  # 최신이 마지막에 오도록

        # 예측값 수집
        front = predict_block_patterns(pattern_list, reverse=False)
        back = predict_block_patterns(pattern_list, reverse=True)

        # 상위 5개 예측값 추출
        front_top5 = [x[0] for x in Counter(front).most_common(5)]
        back_top5 = [x[0] for x in Counter(back).most_common(5)]

        return jsonify({
            "predict_round": len(pattern_list),
            "front_predictions": front_top5,
            "back_predictions": back_top5
        })

    except Exception as e:
        print("[예측 오류]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
