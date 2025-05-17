from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

def load_data():
    try:
        df = pd.read_csv("ladder_results.csv")
        df.dropna(inplace=True)
        return df
    except Exception as e:
        return None

def preprocess(df):
    return df['결과'].tolist()[-1000:]

def transform_to_pattern(block):
    convert = {
        '좌': '3', '우': '4',
        '홀': '홀', '짝': '짝'
    }
    return ''.join(convert.get(ch, '') for ch in block)

def extract_blocks(data, reverse=False):
    results = []
    for size in range(2, 7):
        blocks = []
        for i in range(len(data) - size):
            block = data[i:i+size]
            if reverse:
                block = list(reversed(block))
            pattern_key = ','.join(transform_to_pattern(x) for x in block[:(size * 2) // 3])
            target = block[0]  # 상단 예측
            blocks.append((pattern_key, target))
        results.append(blocks)
    return results

def get_top_predictions(blocks):
    from collections import Counter
    counter = Counter()
    for group in blocks:
        for pattern_key, target in group:
            counter[target] += 1
    return [x[0] for x in counter.most_common(5)]

@app.route("/predict")
def predict():
    df = load_data()
    if df is None:
        return jsonify({
            "round": None,
            "top_predictions": [],
            "bottom_predictions": []
        })

    data = preprocess(df)
    if len(data) < 10:
        return jsonify({
            "round": len(data),
            "top_predictions": [],
            "bottom_predictions": []
        })

    # 앞 기준 (정방향)
    forward_blocks = extract_blocks(data, reverse=False)
    top_predictions = get_top_predictions(forward_blocks)

    # 뒤 기준 (역방향)
    backward_blocks = extract_blocks(data, reverse=True)
    bottom_predictions = get_top_predictions(backward_blocks)

    return jsonify({
        "round": len(data),
        "top_predictions": top_predictions,
        "bottom_predictions": bottom_predictions
    })

if __name__ == "__main__":
    app.run(debug=True)
