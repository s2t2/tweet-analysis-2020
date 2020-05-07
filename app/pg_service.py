
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv() #> loads contents of the .env file into the script's environment

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", default="localhost")
DB_NAME = os.getenv("DB_NAME", default="impeachment_analysis")

DESTRUCTIVE_MIGRATIONS = (os.getenv("DESTRUCTIVE_MIGRATIONS") == "true")

if __name__ == "__main__":

    connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    print("CONNECTION:", connection)

    cursor = connection.cursor()
    print("CURSOR:", cursor)


    sql = ""
    if DESTRUCTIVE_MIGRATIONS:
        sql += "DROP TABLE IF EXISTS user_friends; "
    sql += f"""
        CREATE TABLE IF NOT EXISTS user_friends` (
            user_id int,
            screen_name STRING,
            friend_count INT64,
            friend_names ARRAY<STRING>,
            start_at TIMESTAMP,
            end_at TIMESTAMP
        );
    """


    breakpoint()


    cursor.execute('SELECT * from my_table;')
    result = cursor.fetchall()
    print("RESULT:", type(result))
    print(result)

    connection.close()
