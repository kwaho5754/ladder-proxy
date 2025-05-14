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

    # 가장 최근 회차 찾기
    last_round = max(int(item["date_round"]) for item in data)
    predict_round = last_round + 1

    # 예측값 샘플 - 실제로는 머신 결과로 대체 가능
    predictions = ["좌삼짝", "우삼홀", "좌사홀"]

    return jsonify({
        "predict_round": predict_round,
        "predictions": predictions
    })

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
