from playwright.sync_api import sync_playwright, expect

STATE_PATH = "storage_state.json"

def test_reuse_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        page.goto("http://localhost:8000/index.html", wait_until="domcontentloaded")
        expect(page.get_by_test_id("profile-menu")).to_be_visible(timeout=5_000)

        page.wait_for_timeout(5000)  # 창 유지

        context.close()
        browser.close()

if __name__ == "__main__":
    test_reuse_state()
