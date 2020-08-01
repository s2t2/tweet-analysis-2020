
import time
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor #, as_completed

from app import SERVER_NAME, SERVER_DASHBOARD_URL
from app.email_service import send_email
from app.friend_collection import (MAX_THREADS, BATCH_SIZE, LIMIT, MIN_ID, MAX_ID,
    user_with_friends, cautiously_initialized_storage_service, generate_timestamp
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
    bq.insert_user_friends([user_with_friends(user_row) for user_row in user_rows])
    print(generate_timestamp(), "|", current_thread().name, "|", "PROCESSED BATCH OF", len(user_rows))
    #lock.release()
    return True

def send_completion_email():
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

if __name__ == "__main__":
    service = cautiously_initialized_storage_service()

    users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)
    print("FETCHED UNIVERSE OF", len(users), "USERS")

    if any(users):
        batches = list(split_into_batches(users))
        print(f"ASSEMBLED {len(batches)} BATCHES OF {BATCH_SIZE}")

        with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
            for batch in batches:
                executor.submit(process_and_save_batch, batch, service)
    else:
        send_completion_email()
        print("yeah")
        time.sleep(1)
        print("yeah")
        time.sleep(1)
        print("yeah")
        time.sleep(12 * 60 * 60) # twelve hours
