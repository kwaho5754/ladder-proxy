
import pandas as pd
from flask import Flask, jsonify
from collections import Counter

app = Flask(__name__)

# 🧩 사다리 결과 CSV 경로
CSV_PATH = "ladder_results.csv"

# ✅ 대칭 변환 매핑 정의
MIRROR_MAP = {
    "좌삼짝": "우삼홀", "좌삼홀": "우삼짝",
    "좌사짝": "우사홀", "좌사홀": "우사짝",
    "우삼짝": "좌삼홀", "우삼홀": "좌삼짝",
    "우사짝": "좌사홀", "우사홀": "좌사짝",
}

# 🔁 대칭 변환 함수
def transform_pattern(block):
    transformed = [MIRROR_MAP.get(item, item) for item in block]
    return transformed

# 🔍 블럭 매칭 함수 (앞 기준 2줄만)
def get_front_prediction(data, block_size=2):
    results = []
    latest_block = data[-block_size:]['result'].tolist()
    transformed_block = transform_pattern(latest_block)

    print("[DEBUG] latest block:", latest_block)
    print("[DEBUG] transformed:", transformed_block)

    for i in range(len(data) - block_size - 1):
        ref_block = data[i:i + block_size]['result'].tolist()
        if transform_pattern(ref_block) == transformed_block:
            next_row = data.iloc[i + block_size]
            results.append(next_row['result'])

    print("[DEBUG] matched results:", results)

    counter = Counter(results)
    most_common = [item for item, count in counter.most_common(1)]
    return most_common

@app.route("/predict")
def predict():
    try:
        df = pd.read_csv(CSV_PATH)
        if len(df) < 10:
            raise ValueError("데이터 부족")

        df = df.tail(1000).reset_index(drop=True)
        predict_round = df.iloc[-1]['date_round'] + 1

        front_preds = get_front_prediction(df)

        return jsonify({
            "predict_round": int(predict_round),
            "front_predictions": front_preds,
            "back_predictions": []
        })
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({
            "predict_round": None,
            "front_predictions": [],
            "back_predictions": [],
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
