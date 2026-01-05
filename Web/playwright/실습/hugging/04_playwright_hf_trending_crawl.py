import re
import csv
import time
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE = "https://huggingface.co"
TRENDING = "https://huggingface.co/papers/trending"
PAPER_RE = re.compile(r"^/papers/\d{4}\.\d{5}$")  # /papers/2512.10685

def text_or_empty(loc):
    try:
        return loc.first.inner_text().strip() if loc.count() else ""
    except Exception:
        return ""

def href_or_empty(loc):
    try:
        return loc.first.get_attribute("href") if loc.count() else ""
    except Exception:
        return ""

def crawl(top_n=20, headless=False):
    rows = []
    with sync_playwright() as p:
        print("[1] launch browser...")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.set_default_timeout(20000)

        print("[2] goto trending:", TRENDING)
        resp = page.goto(TRENDING, wait_until="domcontentloaded")
        print("[3] status:", resp.status if resp else None)
        print("[4] title:", page.title())
        print("[5] url:", page.url)

        page.wait_for_selector("a[href^='/papers/']", timeout=20000)

        # ✅ JS 환경이므로 getAttribute 사용
        hrefs = page.eval_on_selector_all(
            "a[href^='/papers/']",
            "els => els.map(e => e.getAttribute('href')).filter(Boolean)"
        )

        seen = set()
        paper_paths = []
        for h in hrefs:
            if h and PAPER_RE.match(h) and h not in seen:
                seen.add(h)
                paper_paths.append(h)

        paper_paths = paper_paths[:top_n]
        print(f"[6] found papers: {len(paper_paths)}")

        for i, path in enumerate(paper_paths, 1):
            url = urljoin(BASE, path)
            print(f"[7] ({i}/{len(paper_paths)}) open:", url)
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(0.5)

            title = text_or_empty(page.locator("h1"))
            abstract = text_or_empty(page.locator(
                "xpath=//h2[contains(.,'Abstract')]/following-sibling::*[1]"
            ))
            published = text_or_empty(page.locator("text=Published on").first)
            upvote = text_or_empty(page.locator("text=Upvote").first)
            arxiv_page = href_or_empty(page.locator("a:has-text('View arXiv page')"))
            github = href_or_empty(page.locator("a:has-text('GitHub')"))

            rows.append({
                "paper_url": url,
                "title": title,
                "published": published,
                "upvote": upvote,
                "abstract": abstract,
                "arxiv_page": arxiv_page,
                "github": github,
            })
            print("     ok:", title[:60])

        browser.close()
    return rows

def save_csv(rows, out_path="data/hf_trending.csv"):
    Path("data").mkdir(exist_ok=True)
    cols = ["paper_url","title","published","upvote","abstract","arxiv_page","github"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    data = crawl(top_n=20, headless=False)  # 창 보이게
    save_csv(data, "data/hf_trending.csv")
    print(f"[DONE] saved {len(data)} rows -> data/hf_trending.csv")
    input("Press Enter to exit...")
