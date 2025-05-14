from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 조합 이름 매핑
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 예측 회차 계산: 마지막 회차 + 1, 288 넘으면 1로 초기화
def get_predict_round_from_data(data):
    if not data:
        return 1
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except Exception:
        return 1

@app.route("/recent-result", methods=["GET"])
def get_recent_prediction():
    try:
        res = requests.get(DATA_URL)
        data = res.json()

        # 빈 데이터 방지
        if not data:
            return jsonify({"error": "No data available"}), 500

        # 패턴 빈도수 계산
        freq = {}
        for row in data:
            key = (row["start_point"], row["line_count"], row["odd_even"])
            freq[key] = freq.get(key, 0) + 1

        # 가장 많이 나온 조합 3개
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top3 = [convert_pattern_name(*x[0]) for x in sorted_freq[:3]]

        predict_round = get_predict_round_from_data(data)

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
