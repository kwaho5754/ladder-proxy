from flask import Flask, jsonify
from flask_cors import CORS  # CORS 허용

app = Flask(__name__)
CORS(app)  # 모든 출처 허용

@app.route('/predict')
def predict():
    # 테스트용 예측 값
    front = ["우3홀", "좌4홀", "좌3짝", "우4짝", "우5홀"]
    back = ["좌4홀", "우3홀", "우4짝", "좌3홀", "좌2짝"]
    round_number = 199

    return jsonify({
        "front_predictions": front,
        "back_predictions": back,
        "predict_round": round_number
    })

if __name__ == '__main__':
    app.run(debug=True)
