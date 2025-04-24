from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청 허용
logging.basicConfig(level=logging.INFO)

def get_blog_rank(keyword: str, target_blog: str):
    """임시로 고정된 더미 데이터를 반환합니다."""
    # 로그만 찍고 크롤링 시도 없이 더미 데이터 반환
    app.logger.info(f"키워드: {keyword}, 블로그: {target_blog} - 크롤링 비활성화 상태")

    # 테스트용 더미 데이터
    return 5  # 고정된 순위 값 반환

@app.route("/rank", methods=["POST", "GET"])
def rank():
    if request.method == "GET":
        return jsonify({"message": "API is working. Use POST with keyword and blog_name."})

    app.logger.info("RAW body >> %s", request.data)
    app.logger.info("Content-Type >> %s", request.content_type)

    cleaned = (
        request.data.decode("utf-8")
        .replace("\u200b", "")
        .replace("\ufeff", "")
        .strip()
    )

    try:
        data = json.loads(cleaned)
        app.logger.info("Parsed data: %s", data)
    except json.JSONDecodeError as e:
        app.logger.error("JSON 파싱 실패: %s", e)
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    keyword = data.get("keyword")
    blog_name = data.get("blog_name")

    app.logger.info("입력 값: keyword=%s, blog_name=%s", keyword, blog_name)

    if not keyword or not blog_name:
        return jsonify({"error": "keyword와 blog_name은 필수입니다."}), 400

    app.logger.info("크롤링 대신 더미 데이터 반환")
    result = get_blog_rank(keyword, blog_name)
    app.logger.info("결과: %s", result)

    return jsonify({"rank": result})

@app.route("/test", methods=["POST", "GET"])
def test():
    if request.method == "GET":
        return jsonify({"message": "Test API is working"})

    try:
        data = request.get_json(force=True)
        return jsonify({
            "received": data,
            "rank": 5  # 테스트용 고정 값
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
