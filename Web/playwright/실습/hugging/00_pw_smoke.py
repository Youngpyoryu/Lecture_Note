from playwright.sync_api import sync_playwright

URL = "https://huggingface.co/papers/trending"

def main():
    print("[1] starting playwright...")
    with sync_playwright() as p:
        print("[2] launching browser (headful)...")
        browser = p.chromium.launch(headless=False)  # 화면으로 확인
        page = browser.new_page()
        page.set_default_timeout(15000)  # 15초 타임아웃

        print("[3] goto:", URL)
        try:
            resp = page.goto(URL, wait_until="domcontentloaded", timeout=15000)
            print("[4] response status:", resp.status if resp else None)
            print("[5] final url:", page.url)
            print("[6] title:", page.title())
            page.screenshot(path="pw_debug.png", full_page=True)
            print("[7] screenshot saved -> pw_debug.png")
        except Exception as e:
            print("[X] goto failed:", repr(e))

        input("Press Enter to close...")
        browser.close()

if __name__ == "__main__":
    main()
