import re
from playwright.sync_api import sync_playwright, expect

LOGIN_URL = "http://localhost:8000/index.html"
EMAIL = "demo@demo.com"
PASSWORD = "pass1234"

def test_login_basic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=600)  # 느리게
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="domcontentloaded")

        page.get_by_label("Email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)

        page.get_by_role("button", name="로그인").click()

        #  lambda 대신 정규표현식 사용
        expect(page).to_have_url(re.compile(r".*/dashboard"), timeout=5_000)

        #  UI 기반 성공 확인(권장)
        expect(page.get_by_test_id("profile-menu")).to_be_visible(timeout=5_000)

        context.close()
        browser.close()

if __name__ == "__main__":
    test_login_basic()
