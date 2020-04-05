# fetch first batch of 5K-10K from bigquery
# count down and when there's nothing left, fetch again

# for each batch, dispatch a bunch of threads to store them in mini batches of 50
# each thread should do its own insert and maybe not need to coordinate back

import time
from datetime import datetime
from random import choice
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

def process_batch(user_ids):
    print(f"PROCESSING {len(user_ids)} USERS (FROM {min(user_ids)} TO {max(user_ids)})")
    results = []
    for user_id in user_ids:
        result = fetch_friends(user_id, choice([1,3]))
        print(result)
        results.append(result)
    return results

def fetch_friends(user_id, sleep_seconds=10):
    time.sleep(sleep_seconds)
    return {"user_id": user_id, "duration": sleep_seconds, "thread_id": current_thread().name.split("_")[-1]}

if __name__ == "__main__":

    TOTAL_USERS = 300
    BATCH_SIZE = 100

    print("----------------")
    start_at = time.perf_counter()
    user_ids = list(range(1, TOTAL_USERS + 1))
    users_count = len(user_ids)
    print("REMAINING USERS:", users_count)

    print("----------------")
    while len(user_ids) > 0:
        batch = user_ids[0:BATCH_SIZE]
        process_batch(batch)
        user_ids = list(set(user_ids) - set(batch))

    print("----------------")
    end_at = time.perf_counter()
    clock_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {users_count} USERS IN {clock_seconds} SECONDS")
