from playwright.sync_api import sync_playwright

URL = "https://arxiv.org/list/cs.AI/recent"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")

        print("[Finding pagination hints]")
        for a in page.locator("a").all():
            href = a.get_attribute("href") or ""
            if "skip=" in href or "show=" in href:
                print("pagination link:", href)

        print("\n[Lecture Point]")
        print("Playwright is used only to discover URL rules.")
        print("Data collection will NOT use Playwright.")

        browser.close()

if __name__ == "__main__":
    main()
