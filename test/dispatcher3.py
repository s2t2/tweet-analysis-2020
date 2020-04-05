import time
from datetime import datetime
#from random import choice
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

TOTAL_USERS = 1000
BATCH_SIZE = 40

class MockStorageService():
    def __init__(self, total_users=TOTAL_USERS):
        self.total_users = total_users
        self.user_ids = list(range(1, total_users + 1))
        self.processed_ids = []
        self.remaining_ids = self.user_ids

    def get_remaining_users(self, batch_size=BATCH_SIZE):
        batch_of_ids = self.remaining_ids[0:batch_size]
        return batch_of_ids

    def store_results(self, batch_of_ids):
        self.remaining_ids = list(set(self.remaining_ids) - set(batch_of_ids))
        self.processed_ids += batch_of_ids
        return True

if __name__ == "__main__":

    service = MockStorageService()

    print("----------------")
    print("USERS REMAINING:", len(service.remaining_ids))

    start_at = time.perf_counter()
    while service.remaining_ids:
        batch_of_ids = service.get_remaining_users()
        print("PROCESSING", len(batch_of_ids))
        time.sleep(0.1)
        service.store_results(batch_of_ids)

    print("----------------")
    end_at = time.perf_counter()
    clock_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {service.total_users} USERS IN {clock_seconds} SECONDS ({round(service.total_users / clock_seconds * 60.0, 2)} PER MINUTE)")














BATCH_SIZE = 100
MAX_THREADS = 50

def process_batch(user_ids):
    print(f"PROCESSING {len(user_ids)} USERS (FROM {min(user_ids)} TO {max(user_ids)})")


    return results

def fetch_friends(user_id):
    sleep_seconds = 30 # sleep_seconds or choice([1,5,10,30,60])
    time.sleep(sleep_seconds)
    return {"user_id": user_id, "duration": sleep_seconds, "thread_id": current_thread().name.split("_")[-1]}
