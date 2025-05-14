from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/recent-result', methods=['GET'])
def get_recent_result():
    try:
        response = requests.get("https://ntry.com/data/json/games/power_ladder/recent_result.json")
        data = response.json()

        # 오늘 날짜 가져오기
        today = datetime.now().strftime("%Y-%m-%d")

        # 오늘 날짜 기준 마지막 회차 확인
        last_round = 0
        for item in data:
            if item['reg_date'] == today:
                last_round = max(last_round, int(item['date_round']))

        # 예측 회차는 오늘 마지막 회차 + 1
        predict_round = last_round + 1 if last_round > 0 else 1

        # 여기선 그냥 예시 top3 패턴으로 대체
        result = {
            "predict_round": predict_round,
            "top3_patterns": ["좌삼짝", "우삼홀", "우사짝"]
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
