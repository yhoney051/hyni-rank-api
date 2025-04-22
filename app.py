from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_blog_rank(keyword: str, target_blog: str):
    """네이버 블로그 탭에서 target_blog가 몇 위에 노출되는지 반환합니다."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # ▶ Render 컨테이너에 설치된 Chromium 위치 지정
    options.binary_location = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get("https://www.naver.com")
        time.sleep(2)

        search = driver.find_element(By.ID, "query")
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        time.sleep(3)

        # 블로그 탭 이동 (없으면 URL 직접 접근)
        try:
            blog_tab = driver.find_element(By.LINK_TEXT, "블로그")
            blog_tab.click()
            time.sleep(3)
        except Exception:
            driver.get(
                f"https://search.naver.com/search.naver?where=blog&query={keyword}"
            )
            time.sleep(3)

        names = driver.find_elements(By.CSS_SELECTOR, ".user_info > a.name")
        keywords_to_match = [
            w for w in target_blog.replace("-", " ").replace("'", "").split() if len(w) > 1
        ]

        for idx, elem in enumerate(names, 1):
            name_text = elem.text.strip()
            if any(k in name_text for k in keywords_to_match):
                return idx
        return None

    except Exception as e:
        app.logger.exception("크롤링 중 오류", exc_info=e)
        return None

    finally:
        driver.quit()


@app.route("/rank", methods=["POST"])
def rank():
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
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    keyword = data.get("keyword")
    blog_name = data.get("blog_name")

    if not keyword or not blog_name:
        return jsonify({"error": "keyword와 blog_name은 필수입니다."}), 400

    result = get_blog_rank(keyword, blog_name)
    return jsonify({"rank": result})


if __name__ == "__main__":
    app.run(debug=True)