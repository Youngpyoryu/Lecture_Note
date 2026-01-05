import requests

CANDIDATES = [
    "https://huggingface.co/api/papers/trending",
    "https://huggingface.co/api/papers",
    "https://huggingface.co/api/papers?sort=trending",
]

def main():
    s = requests.Session()
    for url in CANDIDATES:
        try:
            r = s.get(url, timeout=15)
            print(f"[GET] {url} -> {r.status_code}")
            print("  content-type:", r.headers.get("content-type"))
            print("  body head:", r.text[:150].replace("\n", " "))
        except Exception as e:
            print(f"[GET] {url} -> EXCEPTION: {e}")

if __name__ == "__main__":
    main()
