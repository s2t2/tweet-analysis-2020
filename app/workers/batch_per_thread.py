

from concurrent.futures import ThreadPoolExecutor #, as_completed

from app.workers.friend_collector import (MAX_THREADS, BATCH_SIZE, LIMIT, MIN_ID, MAX_ID,
    user_with_friends, cautiously_initialized_storage_service, generate_timestamp,
    current_thread, BoundedSemaphore
)

def split_into_batches(all_users, batch_size=BATCH_SIZE):
    """h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks"""
    for i in range(0, len(all_users), batch_size):
        yield all_users[i : i + batch_size]

#def process_batch(user_rows):
#    return [user_with_friends(user_row) for user_row in user_rows]

def process_and_save_batch(user_rows, bq, lock=None):
    print(generate_timestamp(), "|", current_thread().name, "|", "PROCESSING...")
    #lock.acquire()
    bq.append_user_friends([user_with_friends(user_row) for user_row in user_rows])
    print(generate_timestamp(), "|", current_thread().name, "|", "PROCESSED BATCH OF", len(user_rows))
    #lock.release()
    return True

if __name__ == "__main__":
    service = cautiously_initialized_storage_service()

    users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)

    print("FETCHED UNIVERSE OF", len(users), "USERS")

    batches = list(split_into_batches(users))
    print(f"ASSEMBLED {len(batches)} BATCHES OF {BATCH_SIZE}")

    #lock = BoundedSemaphore()

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        #results = executor.map(process_batch, batches)
        #for index, result in enumerate(results):
        #    print("RESULTS... INDEX:", index, "SIZE:", len(result))

        for batch in batches:
            executor.submit(process_and_save_batch, batch, service)
            #executor.submit(process_and_save_batch, batch, service, lock)
