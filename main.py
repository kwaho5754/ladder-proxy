from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3]  # 앞 기준: 2~3줄 블럭만 사용

# 한글 변환 테이블
KOR_MAP = {
    "L": "좌", "R": "우",
    "1": "1", "2": "2", "3": "3", "4": "4",
    "ODD": "홀", "EVEN": "짝"
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

def extract_forward_candidates(data, blocks):
    counter = Counter()
    for size in BLOCK_SIZES:
        for i in range(len(data) - size):
            segment = tuple(encode(row) for row in data[i:i + size])
            if segment in blocks:
                next_row = data[i + size]
                code = encode(next_row)
                counter[code] += 1
    return counter

@app.route('/predict')
def predict():
    data = fetch_data()
    if not data:
        return jsonify({"error": "No data"})

    recent_data = data[-288:]
    forward_blocks = make_forward_blocks(recent_data)
    forward_freq = extract_forward_candidates(recent_data, forward_blocks)

    top_forward = [to_korean(code) for code, _ in forward_freq.most_common(5)]

    return jsonify({
        "예측회차": len(data),
        "앞기준_예측값": top_forward
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
