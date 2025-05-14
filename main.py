from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/recent-result", methods=["GET"])
def recent_result():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    data = response.json()

    latest_round = int(data[0]["date_round"])
    next_round = latest_round + 1

    # 예시 예측값 (임시값으로 테스트 가능)
    predictions = [
        {"start_point": "LEFT", "line_count": "3", "odd_even": "EVEN"},
        {"start_point": "RIGHT", "line_count": "3", "odd_even": "ODD"},
        {"start_point": "LEFT", "line_count": "4", "odd_even": "ODD"},
    ]

    def format_name(p):
        start_map = {"LEFT": "좌", "RIGHT": "우"}
        line_map = {"3": "삼", "4": "사"}
        oe_map = {"ODD": "홀", "EVEN": "짝"}
        return f"{start_map[p['start_point']]}{line_map[p['line_count']]}{oe_map[p['odd_even']]}"

    formatted = [format_name(p) for p in predictions]

    return jsonify({
        "next_round": next_round,
        "predictions": formatted
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
