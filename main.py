from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

KOR_MAP = {
    "L": "좌",
    "R": "우",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "ODD": "홀",
    "EVEN": "짝"
}

def to_korean(code):
    for eng, kor in KOR_MAP.items():
        code = code.replace(eng, kor)
    return code

def fetch_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []

def encode(row):
    return row["start_point"][0] + row["line_count"] + row["odd_even"]

def make_blocks(data, size):
    blocks = {}
    for i in range(len(data) - size):
        block = tuple(encode(data[i + j]) for j in range(size))
        next_row = encode(data[i + size])
        if block not in blocks:
            blocks[block] = []
        blocks[block].append(next_row)
    return blocks

def predict():
    raw_data = fetch_data()
    if len(raw_data) < 10:
        return []
    recent_data = raw_data[-288:]  # 고정된 분석 범위

    forward_predictions = Counter()

    for size in BLOCK_SIZES:
        blocks = make_blocks(recent_data, size)
        recent_block = tuple(encode(recent_data[-size + i]) for i in range(size))
        if recent_block in blocks:
            forward_predictions.update(blocks[recent_block])

    top_forward = [to_korean(code) for code, _ in forward_predictions.most_common(5)]
    return top_forward, len(raw_data)

@app.route("/predict")
def predict_route():
    forward_result, round_num = predict()
    return jsonify({
        "앞기준_예측값": forward_result,
        "예측회차": round_num if round_num else None
    })

if __name__ == "__main__":
    app.run(debug=True)
