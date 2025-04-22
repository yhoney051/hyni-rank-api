from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)


def get_blog_rank(keyword, target_blog):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.naver.com")
        time.sleep(2)

        search = driver.find_element(By.ID, "query")
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        time.sleep(3)

        try:
            blog_tab = driver.find_element(By.LINK_TEXT, "블로그")
            blog_tab.click()
            time.sleep(3)
        except:
            driver.get(f"https://search.naver.com/search.naver?where=blog&query={keyword}")
            time.sleep(3)

        names = driver.find_elements(By.CSS_SELECTOR, ".user_info > a.name")
        keywords_to_match = [word for word in target_blog.replace("-", " ").replace("'", "").split() if len(word) > 1]

        for i, name_elem in enumerate(names, 1):
            name = name_elem.text.strip()
            if any(k in name for k in keywords_to_match):
                return i
        return None
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return None
    finally:
        driver.quit()


@app.route("/rank", methods=["POST"])
def rank():
    data = request.get_json()
    keyword = data.get("keyword")
    blog_name = data.get("blog_name")

    if not keyword or not blog_name:
        return jsonify({"error": "keyword와 blog_name은 필수입니다."}), 400

    rank = get_blog_rank(keyword, blog_name)
    return jsonify({"rank": rank})


if __name__ == "__main__":
    app.run(debug=True)
