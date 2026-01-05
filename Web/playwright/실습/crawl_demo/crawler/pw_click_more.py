from playwright.sync_api import sync_playwright, expect

BASE = "http://127.0.0.1:8000/"
EMAIL = "demo@demo.com"
PW = "pass1234"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page()

        page.goto(BASE)

        # 로그인(UI 개입)
        page.get_by_label("Email").fill(EMAIL)
        page.get_by_label("Password").fill(PW)
        page.get_by_role("button", name="로그인").click()

        # 아이템이 렌더링될 때까지 대기
        expect(page.locator("#items li")).to_have_count(10, timeout=5_000)

        # 더보기 클릭(UI 개입)
        page.get_by_role("button", name="더보기").click()
        expect(page.locator("#items li")).to_have_count(20, timeout=5_000)

        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    main()
