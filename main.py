# ✅ 전체 수정된 main.py (복사 모드)
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

BLOCK_SIZES = [2, 3, 4, 5, 6]

# ✅ 코드 ➝ 한글 변환
KOR_MAP = {
    "L": "좌", "R": "우",
    "1": "1", "2": "2", "3": "3", "4": "4",
    "ODD": "홀", "EVEN": "짝"
}

def to_korean(code):
    for eng, kor in KOR_MAP.items():
        code = code.replace(eng, kor)
    return code

# ✅ 외부 JSON 데이터 불러오기
def fetch_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []

# ✅ 한 줄 인코딩
def encode(row):
    return row["start_point"][0] + row["line_count"] + row["odd_even"]

# ✅ 정방향 블럭 생성 함수 (2~6줄)
def make_forward_blocks(data):
    blocks = []
    for size in BLOCK_SIZES:
        if len(data) >= size:
            segment = data[-size:]
            block = tuple(encode(row) for row in segment)
            blocks.append(block)
    return blocks

# ✅ 전체 블럭들 추출 (지금은 정방향만)
def extract_all_blocks(data, size):
    all_blocks = []
    for i in range(len(data) - size):
        segment = data[i:i+size]
        block = tuple(encode(row) for row in segment)
        all_blocks.append((block, data[i+size]))
    return all_blocks

# ✅ 블럭 비교 및 예측 후보 수집
def find_matches(forward_blocks, data):
    result_counter = Counter()
    for block in forward_blocks:
        size = len(block)
        all_blocks = extract_all_blocks(data, size)
        for b, next_row in all_blocks:
            if b == block:
                result = encode(next_row)
                result_counter[result] += 1
    return result_counter

@app.route("/predict", methods=["GET"])
def predict():
    data = fetch_data()
    if not data:
        return jsonify({"앞기준 예측값": [], "예측회차": None})

    recent_blocks = make_forward_blocks(data)
    forward_results = find_matches(recent_blocks, data[:-1])  # 마지막 줄 제외하고 분석

    top5_forward = [to_korean(code) for code, _ in forward_results.most_common(5)]

    # ✅ 디버깅 출력
    print("🔍 디버깅: 최근 블럭들 (정방향)")
    for block in recent_blocks:
        print("   ▶", block)
    print("🔍 예측 후보 수:", len(forward_results))
    print("🔍 Top5:", top5_forward)

    return jsonify({
        "앞기준 예측값": top5_forward,
        "예측회차": data[-1]["round"] if data else None
    })

# ✅ 포트 설정 포함 (0000번 허용 포함)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
