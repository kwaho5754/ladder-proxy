from flask import Flask, jsonify
import pandas as pd
from collections import Counter

app = Flask(__name__)

def transform_block(block):
    # 좌우대칭 치환
    mapping = {
        '좌3짝': '우3홀', '좌3홀': '우3짝',
        '좌4짝': '우4홀', '좌4홀': '우4짝',
        '좌5짝': '우5홀', '좌5홀': '우5짝',
        '우3짝': '좌3홀', '우3홀': '좌3짝',
        '우4짝': '좌4홀', '우4홀': '좌4짝',
        '우5짝': '좌5홀', '우5홀': '좌5짝',
    }
    return [mapping.get(x, x) for x in block]

def get_prediction():
    try:
        df = pd.read_csv("ladder_results.csv")
        df = df.tail(1000).reset_index(drop=True)

        total_data = len(df)
        if total_data < 10:
            return {"front_predictions": [], "back_predictions": [], "predict_round": total_data}

        front_predictions = []
        # 최근 2줄 블럭
        base_block = df.iloc[-2:]["result"].tolist()
        transformed = transform_block(base_block)

        candidates = []
        for i in range(0, total_data - 2):
            cmp_block = df.iloc[i:i + 2]["result"].tolist()
            if cmp_block == transformed:
                next_row = i + 2
                if next_row < total_data:
                    candidates.append(df.iloc[next_row]["result"])

        counter = Counter(candidates)
        most_common = counter.most_common(5)
        front_predictions = [x[0] for x in most_common]

        return {
            "front_predictions": front_predictions,
            "back_predictions": [],
            "predict_round": total_data
        }

    except Exception as e:
        return {"error": str(e), "front_predictions": [], "back_predictions": [], "predict_round": 0}

@app.route('/predict')
def predict():
    result = get_prediction()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
