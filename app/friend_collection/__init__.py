
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

from app import APP_ENV, SERVER_NAME, SERVER_DASHBOARD_URL
from app.bq_service import BigQueryService, generate_timestamp
from app.email_service import send_email
from app.friend_collection.twitter_scraper import get_friends, VERBOSE_SCRAPER, MAX_FRIENDS

load_dotenv()

MIN_USER_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_USER_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
USERS_LIMIT = os.getenv("USERS_LIMIT") # max number of users to fetch from the db

MAX_THREADS = int(os.getenv("MAX_THREADS", default=3)) # the max number of threads to use, for concurrent processing
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=20)) # the max number of processed users to store in BQ at once (with a single insert API call)

#VERBOSE_COLLECTOR = os.getenv("VERBOSE_COLLECTOR", default="true") == "true"

def user_with_friends(row):
    start_at = generate_timestamp()
    #print(f"{start_at} | {current_thread().name} | {row.user_id}")

    friend_names = sorted(get_friends(row.screen_name))
    end_at = generate_timestamp()
    print(f"{end_at} | {current_thread().name} | {row.user_id} | FRIENDS: {len(friend_names)}")

    return {
        "user_id": row.user_id,
        "screen_name": row.screen_name,
        "friend_count": len(friend_names),
        "friend_names": friend_names,
        "start_at": start_at,
        "end_at": end_at
    }

class FriendCollector:
    def __init__(self, min_user_id=MIN_USER_ID, max_user_id=MAX_USER_ID, users_limit=USERS_LIMIT, max_threads=MAX_THREADS, batch_size=BATCH_SIZE):
        self.bq = BigQueryService.cautiously_initialized()

        self.min_user_id = min_user_id # OK to be None
        self.max_user_id = max_user_id # OK to be None
        self.users_limit = users_limit

        self.max_threads = max_threads
        self.batch_size = batch_size

        self.users = None

        print("-------------------------")
        print("FRIEND COLLECTOR CONFIG...")
        print("  MIN USER ID:", self.min_user_id)
        print("  MAX USER ID:", self.max_user_id)
        print("  USERS LIMIT:", self.users_limit)
        print("  MAX THREADS:", self.max_threads)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")
        print("SCRAPER CONFIG...")
        print("  VERBOSE SCRAPER:", VERBOSE_SCRAPER)
        print("  MAX FRIENDS:", MAX_FRIENDS)
        print("-------------------------")

        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()

    def fetch_users(parameter_list):
        self.users = self.bq.fetch_remaining_users(min_id=self.min_user_id, max_id=self.max_user_id, limit=self.users_limit)
        print("FETCHED UNIVERSE OF", len(users), "USERS")

    def perform(self):
        if not self.users: self.fetch_users()

        with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="THREAD") as executor:
            batch = []
            lock = BoundedSemaphore()
            futures = [executor.submit(user_with_friends, row) for row in users]
            print("FUTURE RESULTS", len(futures))
            for index, future in enumerate(as_completed(futures)):
                result = future.result()

                # OK, so this locking business:
                # ... prevents random threads from clearing the batch, which was causing results to almost never get stored, and
                # ... restricts a thread's ability to acquire access to the batch until another one has released it
                lock.acquire()
                batch.append(result)
                if (len(batch) >= self.batch_size) or (index + 1 >= len(futures)): # when batch is full or is last
                    print(f"SAVING BATCH OF {len(batch)}...")
                    self.bq.insert_user_friends(batch)
                    print("CLEARING BATCH...")
                    batch = []
                lock.release()

    def send_completion_email(self):
        subject = "[Impeachment Tweet Analysis] Friend Collection Complete!"
        html = f"""
            <h3>Nice!</h3>
            <p>Server '{SERVER_NAME}' has completed its work.</p>
            <p>So please shut it off so it can get some rest.</p>
            <p>
                <a href='{SERVER_DASHBOARD_URL}'>{SERVER_DASHBOARD_URL}</a>
            </p>
            <p>Thanks!</p>
        """
        response = send_email(subject, html)
        return response

    def sleep(self):
        print("yeah")
        time.sleep(1)
        print("yeah")
        time.sleep(1)
        print("yeah")
        time.sleep(12 * 60 * 60) # twelve hours, enough time to stop the server before it restarts

if __name__ == "__main__":

    collector = FriendCollector()

    collector.perform()
