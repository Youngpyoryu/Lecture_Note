import re
from playwright.sync_api import sync_playwright, expect

LOGIN_URL = "http://localhost:8000/index.html"
EMAIL = "demo@demo.com"
PASSWORD = "pass1234"
STATE_PATH = "storage_state.json"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.get_by_label("Email").fill(EMAIL)
        page.get_by_label("Password").fill(PASSWORD)
        page.get_by_role("button", name="로그인").click()

        expect(page).to_have_url(re.compile(r".*/dashboard"), timeout=5_000)
        expect(page.get_by_test_id("profile-menu")).to_be_visible(timeout=5_000)

        context.storage_state(path=STATE_PATH)
        context.close()
        browser.close()

if __name__ == "__main__":
    main()
