import requests

ROBOTS_URL = "https://huggingface.co/robots.txt"
TARGET_PATH = "/papers/trending"

def main():
    r = requests.get(ROBOTS_URL, timeout=10)
    print("status:", r.status_code)
    print("----- robots.txt -----")
    print(r.text)

    txt = r.text.lower()
    disallows = []
    agent_all = False

    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("user-agent:"):
            agent_all = (line.split(":", 1)[1].strip() == "*")
        if agent_all and line.startswith("disallow:"):
            disallows.append(line.split(":", 1)[1].strip())

    blocked = any(TARGET_PATH.startswith(d) for d in disallows if d)
    print("\nTarget:", TARGET_PATH)
    print("Disallow rules (User-agent:*):", disallows)
    print("Blocked by robots.txt?:", blocked)

if __name__ == "__main__":
    main()
