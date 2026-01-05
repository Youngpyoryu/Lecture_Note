import requests

ROBOTS_URL = "https://arxiv.org/robots.txt"

def main():
    r = requests.get(ROBOTS_URL, timeout=15)
    r.raise_for_status()

    print("=== robots.txt ===")
    print(r.text[:800])
    print("\n[Lecture Point]")
    print("- Crawl-delay 존재 여부 확인")
    print("- Allow / Disallow 범위 확인")
    print("- 허용된 경로만 수집 대상으로 사용")

if __name__ == "__main__":
    main()
