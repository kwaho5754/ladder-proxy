from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

def fetch_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []

def encode(row):
    return row["start_point"][0] + row["line_count"] + row["odd_even"]

def make_target_blocks(data, reverse=False):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[-size:] if not reverse else list(reversed(data))[-size:]
            block = tuple([encode(row) for row in segment])
            blocks.append((block, size))
    return blocks

def find_matches(all_data, block, size):
    matches = []
    for i in range(len(all_data) - size):
        segment = all_data[i:i+size]
        candidate = tuple([encode(row) for row in segment])
        if candidate == block and i > 0:
            matches.append(encode(all_data[i - 1]))
    return matches

def get_top(predictions, all_data, count=5):
    freq = Counter(predictions)
    result = [val for val, _ in freq.most_common(count)]
    
    # 부족 시 전체 빈도 기준으로 보완
    if len(result) < count:
        all_freq = Counter([encode(row) for row in all_data])
        for val, _ in all_freq.most_common():
            if val not in result:
                result.append(val)
            if len(result) == count:
                break
    return result

@app.route("/predict")
def predict():
    all_data = fetch_data()
    if not all_data or len(all_data) < 10:
        return jsonify({"오류": "데이터 부족"})

    recent_data = all_data[-288:]

    # 🔹 정방향 블럭 분석
    front_predictions = []
    front_blocks = make_target_blocks(recent_data, reverse=False)
    for block, size in front_blocks:
        front_predictions.extend(find_matches(all_data, block, size))
    front_top5 = get_top(front_predictions, all_data, count=5)

    # 🔹 역방향 블럭 분석
    back_predictions = []
    back_blocks = make_target_blocks(recent_data, reverse=True)
    for block, size in back_blocks:
        back_predictions.extend(find_matches(all_data, block, size))
    back_top5 = get_top(back_predictions, all_data, count=5)

    round_number = int(all_data[0]["date_round"]) + 1

    return jsonify({
        "예측회차": round_number,
        "앞방향_예측값": front_top5,
        "뒤방향_예측값": back_top5
    })

if __name__ == '__main__':
    # ✅ 외부 접속 허용
    app.run(debug=True, host="0.0.0.0", port=5000)
