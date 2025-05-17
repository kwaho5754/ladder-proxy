from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3]  # 오직 2줄, 3줄 블럭만 사용

KOR_MAP = {
    "L": "좌",
    "R": "우",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "ODD": "홀",
    "EVEN": "짝",
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
            segment = data[-size:]  # 최신 줄부터 size만큼
            block = tuple(encode(row) for row in segment)
            blocks.append(block)
    return blocks

def find_forward_matches(data, target_blocks):
    matches = []
    for i in range(len(data)):
        for size in BLOCK_SIZES:
            if i + size >= len(data):
                continue
            segment = data[i:i+size]
            block = tuple(encode(row) for row in segment)
            if block in target_blocks:
                next_index = i + size
                if next_index < len(data):
                    matches.append(encode(data[next_index]))
    return matches

@app.route("/predict")
def predict():
    data = fetch_data()
    if not data or len(data) < max(BLOCK_SIZES) + 1:
        return jsonify({"error": "Not enough data"})

    # 블럭 생성 및 매칭
    target_blocks = make_forward_blocks(data)
    forward_matches = find_forward_matches(data, target_blocks)

    # 빈도수 집계 및 Top 5
    forward_counter = Counter(forward_matches)
    top5_forward = [to_korean(code) for code, _ in forward_counter.most_common(5)]

    # 회차 정보 추출
    last_round = data[-1].get("round") if data else "-"

    return jsonify({
        "앞기준_예측값": top5_forward,
        "예측회차": last_round
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
