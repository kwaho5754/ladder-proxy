
from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/recent-result", methods=["GET"])
def recent_result():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()

        # 정수 변환을 통한 최대 회차 계산
        last_round = max(int(entry["date_round"]) for entry in data)
        predict_round = last_round + 1

        # 패턴 이름 변환 함수
        def pattern_name(entry):
            direction = "좌" if entry["start_point"] == "LEFT" else "우"
            lines = entry["line_count"]
            parity = "짝" if entry["odd_even"] == "EVEN" else "홀"
            return f"{direction}{lines}{parity}"

        # 패턴별 빈도수 계산
        freq = {}
        for entry in data:
            name = pattern_name(entry)
            freq[name] = freq.get(name, 0) + 1

        # 가장 많이 나온 패턴 3개 반환
        sorted_patterns = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top3 = [item[0] for item in sorted_patterns[:3]]

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
