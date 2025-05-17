from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 📦 예측 블럭 개수 범위
BLOCK_SIZES = [2, 3, 4, 5, 6]

# 📥 외부 JSON 데이터 로드 함수
def fetch_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []

# 🔍 블럭 패턴 생성 함수 (블럭 리스트 반환)
def make_blocks(data, reverse=False):
    data = list(reversed(data)) if reverse else data[:]
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) > size:
            block = tuple([row["start_point"][0] + row["line_count"] + row["odd_even"] for row in data[:size]])
            blocks.append(block)
    return blocks

# 🧠 과거 블럭 비교 함수 (정방향/역방향 모두 사용)
def find_matches(all_data, target_blocks):
    matches = []
    for i in range(len(all_data) - 6):
        past_segment = all_data[i:i+6]  # 최대 6줄 비교
        for size in BLOCK_SIZES:
            if len(past_segment) >= size:
                block = tuple([row["start_point"][0] + row["line_count"] + row["odd_even"] for row in past_segment[:size]])
                if block in target_blocks:
                    matches.append(all_data[i-1]["start_point"][0] + all_data[i-1]["line_count"] + all_data[i-1]["odd_even"])
                    break
    return matches

# 🔢 상위 빈도수 추출 함수 (중복 제거 후 상위 5개)
def get_top(predictions):
    freq = {}
    for p in predictions:
        freq[p] = freq.get(p, 0) + 1
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_freq[:5]]

@app.route("/predict")
def predict():
    all_data = fetch_data()
    if not all_data or len(all_data) < 10:
        return jsonify({"error": "데이터 없음"})

    # ✅ 앞 기준 (정방향): 최신 2~6줄로 블럭 생성 → 과거 동일 패턴 찾기
    front_blocks = make_blocks(all_data[-288:])  # 최신 기준 블럭 생성
    front_matches = find_matches(all_data, front_blocks)
    front_top5 = get_top(front_matches)

    # ✅ 뒤 기준 (역방향): 가장 끝 2~6줄을 뒤에서부터 블럭 구성 → 과거 동일 패턴 찾기
    reversed_data = list(reversed(all_data[-288:]))
    back_blocks = make_blocks(reversed_data, reverse=True)
    back_matches = find_matches(all_data, back_blocks)
    back_top5 = get_top(back_matches)

    round_number = int(all_data[0]["date_round"]) + 1

    return jsonify({
        "predict_round": round_number,
        "front_predictions": front_top5,
        "back_predictions": back_top5
    })

if __name__ == '__main__':
    # ✅ Railway 외부 접속 허용 설정 포함
    app.run(debug=True, host="0.0.0.0", port=5000)
