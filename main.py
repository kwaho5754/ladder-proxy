import pandas as pd
from collections import Counter
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/predict")
def predict():
    csv_path = "ladder_results.csv"
    if not os.path.exists(csv_path):
        return jsonify({"front_predictions": [], "back_predictions": [], "predict_round": 0})

    df = pd.read_csv(csv_path)
    if len(df) < 3:
        return jsonify({"front_predictions": [], "back_predictions": [], "predict_round": len(df)})

    recent = df.tail(1000).reset_index(drop=True)
    results = recent["result"].tolist()

    def make_blocks(data, size=2):
        blocks = []
        for i in range(len(data) - size):
            block = tuple(data[i:i+size])
            next_item = data[i+size]
            blocks.append((block, next_item))
        return blocks

    # ✅ 최근 2개 패턴을 기준으로 예측
    base_block = tuple(results[-2:])
    blocks = make_blocks(results, size=2)

    candidates = [next_item for block, next_item in blocks if block == base_block]
    counter = Counter(candidates)
    top_predictions = [x[0] for x in counter.most_common(5)]

    return jsonify({
        "front_predictions": top_predictions,
        "back_predictions": [],
        "predict_round": len(df)
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
