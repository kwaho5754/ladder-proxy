from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# 대칭 변환 함수
def transform(block):
    table = str.maketrans('좌우삼사홀짝', '우좌사삼짝홀')
    return [b.translate(table) for b in block]

@app.route('/')
def index():
    return render_template('predictor_for_github_final.html')

@app.route('/predict')
def predict():
    df = pd.read_csv('ladder_results.csv')
    results = df['result'].tolist()

    if len(results) < 3:
        return jsonify({'predict_round': len(results), 'front_predictions': [], 'back_predictions': []})

    pattern_list = results[:-1]  # 마지막 줄 제외
    current_block = results[-3:-1]  # 최근 2줄 기준 블럭
    transformed = transform(current_block)

    # 과거에서 블럭 찾기
    prediction = None
    for i in range(len(pattern_list) - 2):
        if pattern_list[i:i+2] == transformed:
            prediction = pattern_list[i+2]  # 그 다음 줄
            break

    return jsonify({
        'predict_round': len(results),
        'front_predictions': [prediction] if prediction else [],
        'back_predictions': []  # 뒤 기준은 안씀
    })

if __name__ == '__main__':
    app.run(debug=True)
