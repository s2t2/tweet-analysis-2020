
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor #, as_completed

from app import fmt_ts
from app.friend_collection import FriendCollector, user_with_friends

class FriendCollectorBatchPerThread(FriendCollector):

    def split_into_batches(all_users, batch_size):
        # h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for i in range(0, len(all_users), batch_size):
            yield all_users[i : i + batch_size]

    def perform(self):
        if not self.users: self.fetch_users()

        if any(self.users):
            batches = list(split_into_batches(users, self.batch_size))
            print(f"ASSEMBLED {len(batches)} BATCHES OF {BATCH_SIZE}")

            with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="THREAD") as executor:
                for batch in batches:
                    executor.submit(process_and_save_batch, batch, service)
        else:
            self.send_completion_email()
            self.sleep()

        def process_and_save_batch(self, user_rows):
            print(fmt_ts(), "|", current_thread().name, "|", "PROCESSING...")
            self.bq.insert_user_friends([user_with_friends(user_row) for user_row in user_rows])
            print(fmt_ts(), "|", current_thread().name, "|", "PROCESSED BATCH OF", len(user_rows))
            return True

if __name__ == "__main__":

    collector = FriendCollectorBatchPerThread.cautiously_initialized()

    collector.perform()
