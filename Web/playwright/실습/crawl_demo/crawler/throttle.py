import time
import random

def sleep_between_requests(min_sec=0.2, max_sec=0.6):
    time.sleep(random.uniform(min_sec, max_sec))
