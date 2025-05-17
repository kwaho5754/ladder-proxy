from flask import Flask
import requests
from collections import Counter

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글깨짐 방지 설정 (추가로 유지)

# 예측 문자열 생성 (한글 조합)
def convert_result(item):
    direction = item["start_point"].upper()
    count = str(item["line_count"])
    odd_even = item["odd_even"].upper()

    dir_str = "좌" if direction == "LEFT" else "우"
    oe_str = "홀" if odd_even == "ODD" else "짝"
    return f"{dir_str}{count}{oe_str}"

# 블럭 추출 함수
def extract_block(data, start, size):
    if start + size > len(data):
        return None
    return tuple(data[start:start+size])

# 블럭 비교 함수
def find_matching_results(data, target_block, block_size, mode):
    matches = []
    for i in range(len(data) - block_size):
        block = extract_block(data, i, block_size)
        if block == target_block:
            if mode == "front" and i > 0:
                matches.append(data[i - 1])
            elif mode == "back" and i + block_size < len(data):
                matches.append(data[i + block_size])
    return matches

# 예측 로직
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
        # 앞 기준
        front_block = tuple(full_data[-block_size:])
        front_matches = find_matching_results(full_data, front_block, block_size, mode="front")
        front_results.extend(front_matches)

        # 뒤 기준
        if len(full_data) > block_size + 1:
            back_block = tuple(full_data[-block_size-1:-1])
            back_matches = find_matching_results(full_data, back_block, block_size, mode="back")
            back_results.extend(back_matches)

    front_top5 = [x[0] for x in Counter(front_results).most_common(5)]
    back_top5 = [x[0] for x in Counter(back_results).most_common(5)]

    return front_top5, back_top5, predict_round

# API 라우터
@app.route("/predict")
def predict():
    front_predictions, back_predictions, predict_round = fetch_and_predict()

    # ✅ 콘솔 출력 (디버깅용)
    print("✅ FRONT:", front_predictions)
    print("✅ BACK:", back_predictions)
    print("✅ ROUND:", predict_round)

    # ✅ 있는 그대로 딕셔너리 리턴
    return {
        "front_predictions": front_predictions,
        "back_predictions": back_predictions,
        "predict_round": predict_round
    }

# 실행
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
