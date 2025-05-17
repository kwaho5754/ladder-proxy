from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/predict')
def predict():
    try:
        # 최신 288개 결과 가져오기
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()

        ladder_data = [
            f"{'R' if row['start_point'] == 'RIGHT' else 'L'}{row['line_count']}{'홀' if row['odd_even'] == 'ODD' else '짝'}"
            for row in data
        ]

        # 정방향: 앞 기준 (2~6줄)
        forward_counts = {}
        for size in range(2, 7):
            recent_block = ladder_data[-size:]
            for i in range(len(ladder_data) - size):
                if ladder_data[i:i+size] == recent_block:
                    next_idx = i + size
                    if next_idx < len(ladder_data):
                        val = ladder_data[next_idx]
                        forward_counts[val] = forward_counts.get(val, 0) + 1

        # 역방향: 뒤 기준 (2~6줄)
        backward_counts = {}
        for size in range(2, 7):
            recent_block = ladder_data[-size:]
            for i in range(len(ladder_data) - size):
                start = len(ladder_data) - i - size
                end = len(ladder_data) - i
                if ladder_data[start:end] == recent_block:
                    prior_idx = start - 1
                    if prior_idx >= 0:
                        val = ladder_data[prior_idx]
                        backward_counts[val] = backward_counts.get(val, 0) + 1

        # 정렬 및 부족 시 보완
        def get_top(pred_dict, used):
            top = sorted(pred_dict.items(), key=lambda x: x[1], reverse=True)
            result = []
            for val, _ in top:
                if val not in used:
                    result.append(val)
                    used.add(val)
                if len(result) >= 5:
                    break
            return result

        used_set = set()
        front_predictions = get_top(forward_counts, used_set)
        back_predictions = get_top(backward_counts, used_set)

        # 부족할 경우 전체 빈도에서 보완
        if len(front_predictions) + len(back_predictions) < 10:
            freq = {}
            for val in ladder_data:
                freq[val] = freq.get(val, 0) + 1
            fallback = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            for val, _ in fallback:
                if val not in used_set:
                    if len(front_predictions) < 5:
                        front_predictions.append(val)
                    else:
                        back_predictions.append(val)
                    used_set.add(val)
                if len(front_predictions) + len(back_predictions) >= 10:
                    break

        # ✅ 'R' → '우', 'L' → '좌' 변환
        front_predictions = [v.replace('R', '우').replace('L', '좌') for v in front_predictions]
        back_predictions = [v.replace('R', '우').replace('L', '좌') for v in back_predictions]

        # 예측 회차는 최신값 +1
        latest_round = max(row['date_round'] for row in data)
        predict_round = latest_round + 1

        return jsonify({
            "front_predictions": front_predictions,
            "back_predictions": back_predictions,
            "predict_round": predict_round
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# Railway 외부 접속 허용
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
