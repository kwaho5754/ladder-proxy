from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

# 코드 → 한글 변환 테이블
KOR_MAP = {
    "L": "좌",
    "R": "우",
    "1": "1", "2": "2", "3": "3", "4": "4",
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

def make_forward_blocks(data):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[-size:]
            block = tuple(encode(row) for row in segment)
            blocks.append(block)
    return blocks

def predict_forward(data):
    all_blocks = []
    for size in BLOCK_SIZES:
        for i in range(len(data) - size):
            segment = data[i:i+size]
            block = tuple(encode(row) for row in segment)
            result = encode(data[i+size])
            all_blocks.append((block, result))
    return all_blocks

@app.route('/predict', methods=['GET'])
def predict():
    data = fetch_data()
    if not data or len(data) < 10:
        return jsonify({
            "앞기준 예측값": [],
            "예측회차": None
        })

    current_blocks = make_forward_blocks(data)
    past_blocks = predict_forward(data)

    match_counter = Counter()
    for curr in current_blocks:
        for past, result in past_blocks:
            if curr == past:
                match_counter[result] += 1

    top_forward = [to_korean(code) for code, _ in match_counter.most_common(5)]

    round_number = data[-1]["date_round"] if "date_round" in data[-1] else None
    return jsonify({
        "앞기준 예측값": top_forward,
        "예측회차": round_number
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
