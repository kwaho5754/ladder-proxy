from flask import Flask, jsonify
import requests
from collections import Counter

app = Flask(__name__)

# 예측 로직 (단순 빈도 기반)
def fetch_and_predict():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    if response.status_code != 200:
        return [], [], None

    try:
        data = response.json()
        # 변환: LEFT/RIGHT + 홀/짝 조합
        combined = [d["start_point"].upper() + d["line_count"] + d["odd_even"] for d in data]
        # 가장 많이 나온 상위 10개 조합 추출
        freq = Counter(combined).most_common(10)
        top10 = [v[0] for v in freq]
        # 앞 기준, 뒤 기준 5개씩 분리
        front_top5 = top10[:5]
        back_top5 = top10[5:]
        predict_round = data[0]["date_round"] + 1 if data else None
        return front_top5, back_top5, predict_round
    except Exception:
        return [], [], None

@app.route("/predict")
def predict():
    front_predictions, back_predictions, predict_round = fetch_and_predict()
    return jsonify({
        "front_top5": front_predictions,
        "back_top5": back_predictions,
        "predict_round": predict_round
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
