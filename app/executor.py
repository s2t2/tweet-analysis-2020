# super h/t: https://www.youtube.com/watch?v=IEEhzQoKtQU

import os
import time
import random
from dotenv import load_dotenv

from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
from threading import Thread, current_thread

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", 5)) # heroku supports max 256, see: https://devcenter.heroku.com/articles/dynos#process-thread-limits

def fetch_friends(user_id, sleep_seconds=1):
    thread_id = current_thread().name

    #print(user_id, "SLEEPING...")
    time.sleep(sleep_seconds)
    #print(user_id, "DONE")
    return {"user_id": user_id, "thread_id": thread_id, "duration": sleep_seconds}

if __name__ == "__main__":

    user_ids = range(0,25)
    start_at = time.perf_counter()
    print(f"USERS: {len(user_ids)}")
    print(f"THREADS: {MAX_THREADS}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THR") as executor:
        #print("EXECUTOR:", type(executor))

        #results = executor.map(fetch_friends, user_ids, random.choice([1,5]))
        #for result in results:
        #    print(result)

        #futures = [executor.submit(fetch_friends, user_id, random.choice([1,5])) for user_id in user_ids]
        #for future in futures:
        #    print(future.result())

        futures = [executor.submit(fetch_friends, user_id, random.choice([1,5])) for user_id in user_ids]
        for future in as_completed(futures):
            print(future.result())

    end_at = time.perf_counter()
    print(f"PROCESSED {len(user_ids)} IN {round(end_at - start_at, 2)} SECONDS")
