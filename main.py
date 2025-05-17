# main.py
from flask import Flask, jsonify
import requests
import pandas as pd
from collections import Counter

app = Flask(__name__)

# 변환 함수 정의
def convert_pattern(block):
    result = []
    for val in block:
        if "좌" in val:
            result.append(val.replace("좌", "우"))
        elif "우" in val:
            result.append(val.replace("우", "좌"))
    return result

# 상단값 추출 함수
def get_upper_result(matches, block_size):
    results = []
    for match in matches:
        index = match[0]
        if index - block_size >= 0:
            results.append(data[index - block_size])
    return results

# 패턴 블럭 추출 함수
def extract_blocks(data, reverse=False):
    blocks = []
    max_index = len(data) - 1
    for block_size in range(2, 7):
        for i in range(len(data) - block_size):
            if reverse:
                block = convert_pattern(data[i + 1:i + 1 + block_size])
                for j in range(i + block_size, len(data) - block_size):
                    comp = convert_pattern(data[j + 1:j + 1 + block_size])
                    if block == comp:
                        blocks.append((j + 1 + block_size - 1, block_size))
            else:
                block = data[i:i + block_size]
                for j in range(i + block_size, len(data) - block_size):
                    comp = data[j:j + block_size]
                    if block == comp:
                        blocks.append((j + block_size - 1, block_size))
    return blocks

# 예측값 계산 함수
def calculate_predictions(data, reverse=False):
    all_predictions = []
    for block_size in range(2, 7):
        if reverse:
            blocks = extract_blocks(data, reverse=True)
        else:
            blocks = extract_blocks(data, reverse=False)
        predictions = get_upper_result(blocks, block_size)
        all_predictions.extend(predictions)
    counter = Counter(all_predictions)
    most_common = counter.most_common(5)
    return [item[0] for item in most_common]

@app.route("/predict")
def predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        raw_data = response.json()["rows"]
        global data
        data = [row["result"] for row in raw_data][::-1][:288]  # 최신순 288개

        forward_top5 = calculate_predictions(data, reverse=False)
        reverse_top5 = calculate_predictions(data, reverse=True)

        # 균형 조합 기반 추천값 계산
        joint = forward_top5 + reverse_top5
        joint_counter = Counter(joint)
        balance = joint_counter.most_common(1)[0][0] if joint_counter else "없음"

        return jsonify({
            "회차": len(raw_data) + 1,
            "앞기준": forward_top5,
            "뒷기준": reverse_top5,
            "균형추천": balance
        })
    except Exception as e:
        return jsonify({
            "회차": "예측 실패",
            "앞기준": [],
            "뒷기준": [],
            "균형추천": "없음",
            "오류": str(e)
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
