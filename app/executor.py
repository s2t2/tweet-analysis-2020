# super h/t: https://www.youtube.com/watch?v=IEEhzQoKtQU

import os
import time
import random
from dotenv import load_dotenv

from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
from threading import Thread, Lock, BoundedSemaphore, current_thread

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=200)) # heroku supports max 256, see: https://devcenter.heroku.com/articles/dynos#process-thread-limits
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=20))

def fetch_friends(user_id, sleep_seconds=1):
    thread_id = int(current_thread().name.replace("THREAD_", "")) + 1
    time.sleep(sleep_seconds)
    return {"thread_id": thread_id, "user_id": user_id, "duration": sleep_seconds}

if __name__ == "__main__":

    user_ids = range(1,111)
    start_at = time.perf_counter()
    print(f"USERS: {len(user_ids)}")
    print(f"THREADS: {MAX_THREADS}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
        #print("EXECUTOR:", type(executor))

        #results = executor.map(fetch_friends, user_ids, random.choice([1,5]))
        #for result in results:
        #    print(result)

        #futures = [executor.submit(fetch_friends, user_id, random.choice([1,5])) for user_id in user_ids]
        #for future in futures:
        #    print(future.result())

        #batch = BoundedSemaphore(5)
        #lock = Lock()

        batch = []
        results = []
        futures = [executor.submit(fetch_friends, user_id, random.choice([1,5,10])) for user_id in user_ids]
        for index, future in enumerate(as_completed(futures)):
            result = future.result()
            print(result)
            batch.append(result)
            results.append(result)

            if len(batch) == BATCH_SIZE:
                print(f"CLEARING BATCH OF {len(batch)}...")
                time.sleep(5)
                batch = []

    end_at = time.perf_counter()
    clock_seconds = round(end_at - start_at, 2)
    total_seconds = sum([result["duration"] for result in results])
    print(f"PROCESSED {len(user_ids)} USERS IN {clock_seconds} SECONDS (OTHERWISE {total_seconds} SECONDS)")
