from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3]

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
            block = tuple([encode(row) for row in segment])
            blocks.append(block)
    return blocks

def make_backward_blocks(data):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[:size]
            block = tuple([encode(row) for row in segment[::-1]])
            blocks.append(block)
    return blocks

def find_predictions(data, blocks):
    candidates = []
    for i in range(len(data)):
        for size in BLOCK_SIZES:
            if i + size < len(data):
                segment = tuple([encode(row) for row in data[i:i+size]])
                if segment in blocks:
                    candidates.append(encode(data[i-1]))
    return candidates

def get_top(predictions, direction):
    counter = Counter(predictions)
    print(f"[{direction}] 전체 예측 후보 수: {len(predictions)}")
    for key, value in counter.most_common():
        print(f"[{direction}] 후보: {key} ➝ {value}회")
    top = [to_korean(pred[0]) + to_korean(pred[1]) + to_korean(pred[2]) for pred, _ in counter.most_common(5)]
    print(f"[{direction}] 최종 예측 Top: {top}")
    return top

@app.route("/predict")
def predict():
    raw_data = fetch_data()
    if not raw_data:
        return jsonify({"예측회차": None, "앞방향_예측값": [], "뒤방향_예측값": []})

    data = raw_data[-288:]
    forward_blocks = make_forward_blocks(data)
    backward_blocks = make_backward_blocks(data[::-1])

    forward_preds = find_predictions(data, forward_blocks)
    backward_preds = find_predictions(data[::-1], backward_blocks)

    top_forward = get_top(forward_preds, "앞")
    top_backward = get_top(backward_preds, "뒤")

    round_number = 100 + len(raw_data)  # 예시 기준 회차
    return jsonify({
        "예측회차": round_number,
        "앞방향_예측값": top_forward,
        "뒤방향_예측값": top_backward
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
