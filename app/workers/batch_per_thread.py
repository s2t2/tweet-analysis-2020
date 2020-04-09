

from concurrent.futures import ThreadPoolExecutor #, as_completed

from app.workers.friend_collector import MAX_THREADS, BATCH_SIZE, LIMIT, user_with_friends, cautiously_initialized_storage_service

def split_into_batches(all_users, batch_size=BATCH_SIZE):
    """h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks"""
    for i in range(0, len(all_users), batch_size):
        yield all_users[i : i + batch_size]

def process_batch(user_rows):
    return [user_with_friends(user_row) for user_row in user_rows]

if __name__ == "__main__":
    service = cautiously_initialized_storage_service()

    users = service.fetch_remaining_users(limit=LIMIT)
    print("FETCHED UNIVERSE OF", len(users), "USERS")

    batches = list(split_into_batches(users))
    print(f"ASSEMBLED {len(batches)} BATCHES OF {BATCH_SIZE}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        results = executor.map(process_batch, batches)
        #for index, result in enumerate(results):
        #    print("RESULTS... INDEX:", index, "SIZE:", len(result))
