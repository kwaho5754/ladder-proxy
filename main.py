from flask import Flask, jsonify
import pandas as pd
from collections import Counter

app = Flask(__name__)

# 패턴 변환 매핑 테이블 (예: 좌삼짝 -> 우삼홀)
SYMMETRY_MAP = {
    '좌삼짝': '우삼홀', '우삼홀': '좌삼짝',
    '좌사홀': '우사짝', '우사짝': '좌사홀'
}

# 패턴 변환 함수 (대칭 변환)
def transform_to_symmetry(pattern):
    return SYMMETRY_MAP.get(pattern, pattern)

# 블럭 예측 (정방향 흐름 기준)
def predict_by_flow(pattern_list, block_size):
    if len(pattern_list) < block_size:
        return "없음"
    block = pattern_list[:block_size]             # 정방향 조립
    partial = block[:block_size - 1]              # 상단 기준 블럭
    transformed = [transform_to_symmetry(p) for p in partial if transform_to_symmetry(p)]

    # 전체에서 과거 블럭 비교
    candidates = []
    for i in range(len(pattern_list) - block_size):
        window = pattern_list[i:i + block_size - 1]
        if window == transformed:
            candidates.append(pattern_list[i + block_size - 1])  # 블럭의 상단

    if not candidates:
        return "없음"
    return Counter(candidates).most_common(1)[0][0]

# 블럭 예측 (역방향 흐름 기준)
def predict_by_reverse_flow(pattern_list, block_size):
    if len(pattern_list) < block_size:
        return "없음"
    block = pattern_list[:block_size][::-1]       # 역방향 조립
    partial = block[:block_size - 1]              # 상단 기준 블럭
    transformed = [transform_to_symmetry(p) for p in partial if transform_to_symmetry(p)]

    # 전체에서 과거 블럭 비교
    candidates = []
    for i in range(len(pattern_list) - block_size):
        window = pattern_list[i:i + block_size - 1]
        if window == transformed:
            candidates.append(pattern_list[i + block_size - 1])  # 블럭의 상단

    if not candidates:
        return "없음"
    return Counter(candidates).most_common(1)[0][0]

# 예측 API
@app.route("/predict")
def predict():
    try:
        df = pd.read_csv("ladder_results.csv")
        pattern_list = df['결과'].tolist()[::-1]  # 최신 기준 역순 정렬

        # 앞 기준 Top1~5 (정방향 흐름)
        forward_predictions = [
            predict_by_flow(pattern_list, i) for i in range(2, 7)
        ]

        # 뒤 기준 Top6~10 (역방향 흐름)
        reverse_predictions = [
            predict_by_reverse_flow(pattern_list, i) for i in range(2, 7)
        ]

        return jsonify({
            "회차": len(df) + 1,
            "앞기준": forward_predictions,
            "뒤기준": reverse_predictions
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
