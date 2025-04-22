from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route("/rank", methods=["POST"])
def get_blog_rank():
    try:
        data = request.get_json(force=True)
        keyword = data.get("keyword")
        blog_name = data.get("blog_name")

        if not keyword or not blog_name:
            return jsonify({"error": "Missing keyword or blog_name"}), 400

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        url = f"https://search.naver.com/search.naver?where=post&query={keyword}"
        driver.get(url)
        time.sleep(2)

        blog_elements = driver.find_elements(By.CSS_SELECTOR, "a.sh_blog_title")
        rank = -1
        for idx, elem in enumerate(blog_elements, start=1):
            title = elem.get_attribute("title")
            href = elem.get_attribute("href")
            if blog_name in title or blog_name in href:
                rank = idx
                break

        driver.quit()
        return jsonify({"rank": rank})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
