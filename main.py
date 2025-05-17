from flask import Flask, jsonify
from flask_cors import CORS
import requests
import pandas as pd
from collections import Counter

app = Flask(__name__)
CORS(app)

URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

def extract_predictions_forward(data, size):
    front_block = data[-size:]
    candidates = []
    for i in range(len(data) - size):
        block = data[i:i+size]
        if block == front_block and i+size < len(data):
            candidates.append(data[i+size])
    return candidates

def extract_predictions_backward(data, size):
    reversed_data = data[::-1]
    back_block = reversed_data[-size:]
    candidates = []
    for i in range(len(reversed_data) - size):
        block = reversed_data[i:i+size]
        if block == back_block and i+size < len(reversed_data):
            candidates.append(reversed_data[i+size])
    return candidates

@app.route('/predict')
def predict():
    try:
        res = requests.get(URL)
        json_data = res.json()
        results = [f"{row['start_point'][0]}{row['line_count']}{'홀' if row['odd_even']=='ODD' else '짝'}" for row in json_data]
        data = results[::-1][:288]

        forward_preds = []
        backward_preds = []

        for size in range(2, 7):
            forward_preds += extract_predictions_forward(data, size)
            backward_preds += extract_predictions_backward(data, size)

        front_counter = Counter(forward_preds)
        back_counter = Counter(backward_preds)

        top5_front = [x[0] for x in front_counter.most_common(5)]
        top5_back = [x[0] for x in back_counter.most_common(5)]

        next_round = json_data[0]['date_round'] + 1

        return jsonify({
            "front_predictions": top5_front,
            "back_predictions": top5_back,
            "predict_round": next_round
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # 🚨 Railway 배포 시 반드시 포트와 호스트 지정
    app.run(debug=True, host='0.0.0.0', port=5000)
