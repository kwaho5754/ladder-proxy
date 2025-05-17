from flask import Flask, jsonify
from flask_cors import CORS
import os  # ✅ 포트 지정용

app = Flask(__name__)
CORS(app)  # 모든 출처 허용

@app.route('/predict')
def predict():
    # 테스트 예측 결과
    front = ["우3홀", "좌4홀", "좌3짝", "우4짝", "우5홀"]
    back = ["좌4홀", "우3홀", "우4짝", "좌3홀", "좌2짝"]
    round_number = 199

    return jsonify({
        "front_predictions": front,
        "back_predictions": back,
        "predict_round": round_number
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # ✅ Railway 포트 반영
    app.run(host='0.0.0.0', port=port, debug=True)
