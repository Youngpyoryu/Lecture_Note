import time
import random
import requests

TIMEOUT = 10
MAX_RETRIES = 3
BASE_BACKOFF = 0.6

def request_with_retry(session, method, url, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.request(method, url, timeout=TIMEOUT, **kwargs)

            if resp.status_code == 429:
                wait = BASE_BACKOFF * (2 ** (attempt - 1))
                time.sleep(wait)
                continue

            if 500 <= resp.status_code < 600:
                raise requests.HTTPError(resp.status_code)

            return resp

        except Exception as e:
            wait = BASE_BACKOFF * (2 ** (attempt - 1))
            wait *= random.uniform(0.9, 1.1)
            time.sleep(wait)

    raise RuntimeError("Max retry exceeded")
