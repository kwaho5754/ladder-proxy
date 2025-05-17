from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

# 영어 코드 -> 한글 변환 테이블
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

def analyze_forward(data):
    blocks = make_forward_blocks(data)
    candidates = []
    for size in BLOCK_SIZES:
        for i in range(len(data) - size):
            window = tuple(encode(row) for row in data[i:i + size])
            if window in blocks:
                if i + size < len(data):
                    candidates.append(encode(data[i + size]))
    return Counter(candidates)

@app.route("/predict")
def predict():
    data = fetch_data()
    if not data:
        return jsonify({"error": "데이터 없음"})

    예측회차 = data[-1].get("date_round") if data else None
    분석대상 = data[-288:]  # 항상 최신 288개만 사용

    forward_counter = analyze_forward(분석대상)
    forward_top5 = [to_korean(code) for code, _ in forward_counter.most_common(5)]

    return jsonify({
        "앞방향_예측값": forward_top5,
        "예측회차": 예측회차
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
