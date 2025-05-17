from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3]  # 2줄, 3줄 블럭만 사용

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

def make_blocks(data, reverse=False):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[-size:] if not reverse else data[:size]
            block = tuple(encode(row) for row in segment)
            blocks.append(block[::-1] if reverse else block)
    return blocks

def find_matches(data, target_blocks, reverse=False):
    candidates = []
    data_range = range(len(data))
    for i in data_range:
        for size in BLOCK_SIZES:
            if i + size < len(data):
                block = tuple(encode(data[i + j]) for j in range(size))
                if reverse:
                    block = block[::-1]
                if block in target_blocks:
                    next_index = i - 1 if reverse else i + size
                    if 0 <= next_index < len(data):
                        candidates.append(encode(data[next_index]))
    return Counter(candidates)

@app.route("/predict")
def predict():
    data = fetch_data()
    if len(data) < 10:
        return jsonify({"error": "데이터 부족"})

    forward_blocks = make_blocks(data[-288:], reverse=False)
    backward_blocks = make_blocks(data[-288:], reverse=True)

    forward_counter = find_matches(data[:-1], forward_blocks, reverse=False)
    backward_counter = find_matches(data[:-1], backward_blocks, reverse=True)

    print("\n[디버깅] 앞 블럭:", forward_blocks, flush=True)
    print("[디버깅] 뒤 블럭:", backward_blocks, flush=True)
    print("[디버깅] 앞 후보 수:", len(forward_counter), flush=True)
    print("[디버깅] 뒤 후보 수:", len(backward_counter), flush=True)

    top_forward = [to_korean(code) for code, _ in forward_counter.most_common(5)]
    top_backward = [to_korean(code) for code, _ in backward_counter.most_common(5)]

    return jsonify({
        "앞방향_예측값": top_forward,
        "뒤방향_예측값": top_backward,
        "예측회차": len(data)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
