import requests
from collections import Counter
from flask import Flask, jsonify

app = Flask(__name__)

URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 변환 함수 (좌/우 + 줄수 + 홀짝 조합)
def transform_result(row):
    return f"{row['start_point']}{row['line_count']}{row['odd_even']}", row['date_round']

def get_recent_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        raw_data = response.json()
        transformed = [transform_result(row) for row in raw_data]
        return transformed[:288]  # 최근 288개 고정
    except Exception as e:
        print(f"[ERROR] Failed to load or transform data: {e}")
        return []

def block_match(data, direction):
    predictions = []
    seen_blocks = {}
    base_sizes = range(2, 7)  # 블럭 크기: 2줄 ~ 6줄

    if direction == "front":
        for block_size in base_sizes:
            base_block = [pattern for pattern, _ in data[-block_size:]]
            for i in range(len(data) - block_size):
                comp_block = [pattern for pattern, _ in data[i:i+block_size]]
                if base_block == comp_block:
                    next_index = i + block_size  # 다음 줄
                    if next_index < len(data):
                        candidate = data[next_index][0]
                        seen_blocks[data[i][1]] = candidate

    elif direction == "back":
        for block_size in base_sizes:
            base_block = [pattern for pattern, _ in data[:block_size]]
            for i in range(block_size, len(data)):
                comp_block = [pattern for pattern, _ in data[i-block_size:i]]
                if base_block == comp_block:
                    prev_index = i - block_size - 1  # 이전 줄
                    if prev_index >= 0:
                        candidate = data[prev_index][0]
                        seen_blocks[data[i-block_size][1]] = candidate

    sorted_preds = sorted(seen_blocks.items(), key=lambda x: -int(x[0]))
    return [v for _, v in sorted_preds[:5]]  # 최근 순서로 최대 5개

@app.route("/predict")
def predict():
    data = get_recent_data()
    if not data:
        return jsonify({"error": "데이터 없음", "front_predictions": [], "back_predictions": [], "predict_round": None})

    front_predictions = block_match(data, "front")
    back_predictions = block_match(data, "back")
    round_num = data[-1][1] if data else None

    return jsonify({
        "front_predictions": front_predictions,
        "back_predictions": back_predictions,
        "predict_round": round_num
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
