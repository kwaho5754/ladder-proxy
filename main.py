@app.route("/recent-result", methods=["GET"])
def recent_result():
    # 1. 외부 JSON 데이터 가져오기
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    data = response.json()

    # 2. 예시 예측 로직 (최근 결과 기반 상위 3개 패턴 추정)
    # 실제 분석 로직은 여기에 삽입
    predict_1 = data[0]['start_point']  # 가장 최근
    predict_2 = data[1]['start_point']  # 두 번째 최근
    predict_3 = data[2]['start_point']  # 세 번째 최근

    # 3. 결과 리턴
    return jsonify({"predictions": [predict_1, predict_2, predict_3]})
