import pandas as pd
from collections import Counter
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

CSV_PATH = "ladder_results.csv"


def load_recent_data(n=288):
    df = pd.read_csv(CSV_PATH)
    if len(df) < n:
        return df
    return df.tail(n)


def extract_target_column(df):
    if "result" in df.columns:
        return df["result"].tolist()
    return []


def get_top_predictions(target_list, top_n=10):
    counter = Counter(target_list)
    most_common = counter.most_common(top_n)
    return [item[0] for item in most_common]


@app.route("/predict")
def predict():
    try:
        df = load_recent_data()
        targets = extract_target_column(df)
        predictions = get_top_predictions(targets, 10)

        return jsonify({
            "predict_round": len(df),
            "front_predictions": predictions[:5],
            "back_predictions": predictions[5:],
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "predict_round": 0,
            "front_predictions": [],
            "back_predictions": [],
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
