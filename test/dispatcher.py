# fetch first batch of 5K-10K from bigquery
# count down and when there's nothing left, fetch again

# for each batch, dispatch a bunch of threads to store them in mini batches of 50
# each thread should do its own insert and maybe not need to coordinate back

import time
from datetime import datetime
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

def process_users(user_ids):
    print(f"PROCESSING {len(user_ids)} USERS (FROM {min(user_ids)} TO {max(user_ids)})")
    time.sleep(1)
    #results = []
    #with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
    #    futures = [executor.submit(fetch_friends, row) for row in users]
    #    print("FUTURE RESULTS", len(futures))
#
    #    for future in as_completed(futures):
    #        result = future.result()
    #        results.append(result)
    #        print(result)

    #return results

def fetch_friends(user_id, sleep_seconds=10):
    thread_id = int(current_thread().name.replace("THREAD_", "")) + 1
    time.sleep(sleep_seconds)
    return {"thread_id": thread_id, "user_id": user_id, "duration": sleep_seconds}

if __name__ == "__main__":

    print("----------------")
    start_at = time.perf_counter()
    users_count = 300
    print("REMAINING USERS:", users_count)

    print("----------------")
    users_processed = 0
    while users_processed < users_count:
        users = list(range(1, 100 + 1))
        process_users(users)
        users_processed += len(users)
        print(users_processed)

    print("----------------")
    end_at = time.perf_counter()
    clock_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {users_processed} USERS IN {clock_seconds} SECONDS")
