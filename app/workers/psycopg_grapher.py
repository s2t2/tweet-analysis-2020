
#import os
#from dotenv import load_dotenv
import psycopg2

#load_dotenv()

#DATABASE_URL = os.getenv("DATABASE_URL", default="postgresql://username:password@localhost/dbname")
#USER_FRIENDS_TABLE_NAME = os.getenv("USER_FRIENDS_TABLE_NAME", default="user_friends")
#BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=10_000))

from app.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
from app.workers import BATCH_SIZE

if __name__ == "__main__":

    print(USER_FRIENDS_TABLE_NAME, BATCH_SIZE)

    connection = psycopg2.connect(DATABASE_URL)
    print("CONNECTION:", connection)

    cursor = connection.cursor()
    #cursor = connection.cursor(name="MAGIC_CURSOR")
    print("CURSOR:", cursor)

    sql = f"""
        SELECT id, user_id, screen_name, friend_count, friend_names
        FROM {USER_FRIENDS_TABLE_NAME}
    """
    cursor.execute(sql)

    # h/t: https://www.buggycoder.com/fetching-millions-of-rows-in-python-psycopg2/
    while True:
        results = cursor.fetchmany(size=BATCH_SIZE)
        if results:
            print(len(results))
        else:
            break

    cursor.close()
    connection.close()
