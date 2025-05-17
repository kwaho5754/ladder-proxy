import requests
from collections import Counter
from flask import Flask, jsonify

app = Flask(__name__)

# 항상 288개 고정된 데이터 URL
DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"


def fetch_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        return response.json()  # 리스트 형태 반환
    except Exception as e:
        print("[ERROR] Failed to fetch data:", e)
        return []


def analyze_prediction(data):
    if not data or not isinstance(data, list):
        return [], []

    # 최근 288줄 분석
    recent_data = data[:288]

    pattern_counter = Counter()

    for item in recent_data:
        pattern = f"{item['start_point']}{item['line_count']}{item['odd_even']}"
        pattern_counter[pattern] += 1

    # 가장 많은 순으로 정렬된 예측값
    all_predictions = [x[0] for x in pattern_counter.most_common(10)]

    # 앞 기준 1~5, 뒤 기준 6~10으로 분리
    front_predictions = all_predictions[:5]
    back_predictions = all_predictions[5:10]

    return front_predictions, back_predictions


@app.route("/predict", methods=["GET"])
def predict():
    data = fetch_data()
    front, back = analyze_prediction(data)
    return jsonify({
        "predict_round": len(data),  # 항상 288
        "front_predictions": front,
        "back_predictions": back
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
