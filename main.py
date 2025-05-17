from flask import Flask, jsonify
import requests
from collections import Counter

app = Flask(__name__)

# 🧩 결과 변환 함수
def convert_result(item):
    direction = item["start_point"].upper()  # LEFT / RIGHT
    count = item["line_count"]               # 3 / 4
    odd_even = item["odd_even"].upper()      # ODD / EVEN
    return f"{'좌' if direction == 'LEFT' else '우'}{count}{'홀' if odd_even == 'ODD' else '짝'}"

# 🔍 블럭 추출
def extract_block(data, start, size):
    if start + size > len(data):
        return None
    return tuple(data[start:start+size])

# 🔁 블럭 매칭
def find_matching_results(data, target_block, block_size, mode):
    matches = []
    search_range = range(len(data) - block_size)
    for i in search_range:
        block = extract_block(data, i, block_size)
        if block == target_block:
            if mode == "front" and i > 0:
                matches.append(data[i - 1])  # 위쪽 결과 (정방향)
            elif mode == "back" and i + block_size < len(data):
                matches.append(data[i + block_size])  # 아래쪽 결과 (역방향)
    return matches

# 🔮 예측 로직
def fetch_and_predict():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    if response.status_code != 200:
        return [], [], None

    raw_data = response.json()
    full_data = [convert_result(d) for d in raw_data]
    predict_round = raw_data[0]["date_round"] + 1 if raw_data else None

    front_results, back_results = [], []

    for block_size in range(2, 7):
        # 앞 기준 (정방향): 최신 블럭과 동일한 블럭이 과거에 있으면 → 해당 블럭의 위줄
        front_block = tuple(full_data[-block_size:])
        front_matches = find_matching_results(full_data, front_block, block_size, mode="front")
        front_results.extend(front_matches)

        # 뒤 기준 (역방향): 최신 블럭과 동일한 블럭이 과거에 있으면 → 해당 블럭의 아래줄
        if len(full_data) > block_size + 1:
            back_block = tuple(full_data[-block_size-1:-1])
            back_matches = find_matching_results(full_data, back_block, block_size, mode="back")
            back_results.extend(back_matches)

    # 중복 포함 카운트 → 최다 빈도 기준 Top 5 추출
    front_top5 = [x[0] for x in Counter(front_results).most_common(5)]
    back_top5 = [x[0] for x in Counter(back_results).most_common(5)]

    return front_top5, back_top5, predict_round

# 🔗 API 엔드포인트
@app.route("/predict")
def predict():
    front_predictions, back_predictions, predict_round = fetch_and_predict()
    return jsonify({
        "front_predictions": front_predictions,
        "back_predictions": back_predictions,
        "predict_round": predict_round
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
