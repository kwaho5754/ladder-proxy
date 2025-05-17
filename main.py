from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/predict')
def predict():
    # 예시 결과 — 실제 예측 로직으로 대체
    front = ['우3홀', '좌4홀', '좌3짝', '우4짝', '우5홀']
    back = ['좌4홀', '우3홀', '우4짝', '좌3홀', '좌2짝']
    round_number = 199

    return jsonify({
        "front_predictions": front,
        "back_predictions": back,
        "predict_round": round_number
    })

if __name__ == '__main__':
    app.run(debug=True)
