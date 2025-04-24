from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import json

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청 허용
logging.basicConfig(level=logging.INFO)


def get_blog_rank(keyword: str, target_blog: str):
    """네이버 블로그 탭에서 target_blog가 몇 위에 노출되는지 반환합니다."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Render 컨테이너에 설치된 Chromium 위치 지정
    options.binary_location = "/usr/bin/chromium-browser"

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        app.logger.info("Chrome 드라이버 초기화 성공")
    except Exception as e:
        app.logger.error("Chrome 드라이버 초기화 실패: %s", e)
        return "크롤링 오류: 드라이버 초기화 실패"

    try:
        app.logger.info("네이버 페이지 접속 시도")
        driver.get("https://www.naver.com")
        time.sleep(3)  # 대기 시간 증가

        app.logger.info("검색어 입력: %s", keyword)
        search = driver.find_element(By.ID, "query")
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        time.sleep(4)  # 대기 시간 증가

        # 블로그 탭 이동 (없으면 URL 직접 접근)
        try:
            app.logger.info("블로그 탭 클릭 시도")
            blog_tab = driver.find_element(By.LINK_TEXT, "블로그")
            blog_tab.click()
            time.sleep(4)  # 대기 시간 증가
        except Exception as e:
            app.logger.info("블로그 탭 클릭 실패, URL 직접 접근: %s", e)
            driver.get(
                f"https://search.naver.com/search.naver?where=blog&query={keyword}"
            )
            time.sleep(4)  # 대기 시간 증가

        app.logger.info("블로그 목록 스캔 시작")
        names = driver.find_elements(By.CSS_SELECTOR, ".user_info > a.name")
        app.logger.info("찾은 블로그 수: %d", len(names))

        keywords_to_match = [
            w for w in target_blog.replace("-", " ").replace("'", "").split() if len(w) > 1
        ]
        app.logger.info("검색할 키워드: %s", keywords_to_match)

        for idx, elem in enumerate(names, 1):
            name_text = elem.text.strip()
            app.logger.info("블로그 %d: %s", idx, name_text)
            if any(k in name_text for k in keywords_to_match):
                app.logger.info("일치하는 블로그 발견! 순위: %d", idx)
                return idx

        app.logger.info("일치하는 블로그를 찾지 못함")
        return None
    except Exception as e:
        app.logger.exception("크롤링 중 오류", exc_info=e)
        return "크롤링 오류: " + str(e)
    finally:
        driver.quit()
        app.logger.info("드라이버 종료")


@app.route("/rank", methods=["POST", "GET"])  # GET 메서드도 추가
def rank():
    # GET 요청 처리 (테스트용)
    if request.method == "GET":
        return jsonify({"message": "API is working. Use POST with keyword and blog_name."})

    # 디버그용: 요청 원본과 Content-Type 확인
    app.logger.info("RAW body >> %s", request.data)
    app.logger.info("Content-Type >> %s", request.content_type)

    # 제어문자 제거 후 JSON 파싱
    cleaned = (
        request.data.decode("utf-8")
        .replace("\u200b", "")  # zero‑width space
        .replace("\ufeff", "")  # BOM
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

    # 크롤링 수행
    app.logger.info("크롤링 시작...")
    result = get_blog_rank(keyword, blog_name)
    app.logger.info("크롤링 완료, 결과: %s", result)

    return jsonify({"rank": result})


@app.route("/test", methods=["POST", "GET"])
def test():
    """테스트용 엔드포인트"""
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