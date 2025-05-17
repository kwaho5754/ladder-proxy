from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"


def fetch_recent_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    return []


def build_blocks(data, direction="front", block_size=2):
    blocks = []
    total = len(data)
    rng = range(total - block_size)
    for i in rng:
        if direction == "front":
            block = tuple(data[i + j]["result"] for j in range(block_size))
            next_value = data[i + block_size]["result"]
        elif direction == "back":
            block = tuple(data[i + j]["result"] for j in range(block_size))
            next_value = data[i - 1]["result"] if i > 0 else None
        else:
            continue
        if next_value:
            blocks.append((block, next_value))
    return blocks


def find_matches(data, direction="front", block_size=2):
    if len(data) < block_size + 1:
        return []

    if direction == "front":
        current_block = tuple(data[-block_size + i]["result"] for i in range(block_size))
    else:  # back
        current_block = tuple(data[-(i + 1)]["result"] for i in reversed(range(block_size)))

    block_data = build_blocks(data[:-1], direction, block_size)
    matches = [next_value for block, next_value in block_data if block == current_block]
    return matches


def get_predictions(data, direction):
    all_matches = []
    for size in range(2, 7):  # 블럭 사이즈 2~6
        matches = find_matches(data, direction, block_size=size)
        all_matches.extend(matches)

    if not all_matches:
        return ["데이터 없음"]

    freq = Counter(all_matches)
    ranked = [f"{key}" for key, _ in freq.most_common(5)]
    return ranked


@app.route("/predict")
def predict():
    data = fetch_recent_data()
    if not data:
        return jsonify({"error": "데이터 로드 실패"}), 500

    front_predictions = get_predictions(data, direction="front")
    back_predictions = get_predictions(data, direction="back")
    round_number = int(data[-1]["date_round"]) + 1 if data else 0

    return jsonify({
        "front_predictions": front_predictions,
        "back_predictions": back_predictions,
        "predict_round": round_number
    })


if __name__ == "__main__":
    # Railway에서 외부 접근 허용하려면 host/port 지정 필수
    app.run(debug=True, host="0.0.0.0", port=5000)
