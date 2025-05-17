from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

# 🔤 코드 → 한글 변환 테이블
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
            block = tuple([encode(row) for row in segment])
            blocks.append((block, size))
    return blocks

def make_reverse_blocks(data):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[-size:]
            # 역방향 분석이므로 뒷글자 2개를 기준으로 블럭 구성한다고 가정
            block = tuple([encode(row)[-2:] for row in segment])
            blocks.append((block, size))
    return blocks

def find_matches(all_data, target_block, size, mode="forward"):
    matches = []
    for i in range(len(all_data) - size):
        segment = all_data[i:i+size]
        if mode == "forward":
            block = tuple([encode(row) for row in segment])
        else:  # reverse
            block = tuple([encode(row)[-2:] for row in segment])

        if block == target_block and i > 0:
            matches.append(encode(all_data[i - 1]))  # 바로 윗줄 결과
    return matches

def get_top(predictions, all_data, count=5):
    freq = Counter(predictions)
    result = [val for val, _ in freq.most_common(count)]
    return result

@app.route("/predict")
def predict():
    all_data = fetch_data()
    if not all_data or len(all_data) < 10:
        return jsonify({"오류": "데이터 부족"})

    recent_data = all_data[-288:]

    # ✅ 앞 블럭 분석 (정방향)
    front_predictions = []
    front_blocks = make_forward_blocks(recent_data)
    for block, size in front_blocks:
        front_predictions.extend(find_matches(all_data, block, size, mode="forward"))
    front_top5 = get_top(front_predictions, all_data, count=5)

    # ✅ 뒤 블럭 분석 (역방향)
    back_predictions = []
    back_blocks = make_reverse_blocks(recent_data)
    for block, size in back_blocks:
        back_predictions.extend(find_matches(all_data, block, size, mode="reverse"))
    back_top5 = get_top(back_predictions, all_data, count=5)

    round_number = int(all_data[0]["date_round"]) + 1

    return jsonify({
        "예측회차": round_number,
        "앞방향_예측값": [to_korean(v) for v in front_top5],
        "뒤방향_예측값": [to_korean(v) for v in back_top5]
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
