
import os

from dotenv import load_dotenv

from app.bq_service import BigQueryService

load_dotenv()

USERS_LIMIT = int(os.getenv("USERS_LIMIT", default="1000")) # forces us to have a limit, unlike the app.workers version
TOPIC = os.getenv("TOPIC", default="#MAGA")
START_AT = os.getenv("START_AT", default="2019-01-15 01:00:00") # On 1/15, The House of Representatives names seven impeachment managers and votes to transmit articles of impeachment to the Senate
END_AT = os.getenv("END_AT", default="2020-01-30 01:00:00")

if __name__ == "__main__":

    print("---------------------------------------")
    print("CUSTOM GRAPHER...")
    print(f"  FETCHING {USERS_LIMIT} USERS")
    print(f"  TALKING ABOUT '{TOPIC.upper()}' ")
    print(f"  BETWEEN '{START_AT} AND '{END_AT}'")

    service = BigQueryService.cautiously_initialized()

    results = service.fetch_random_users(limit=USERS_LIMIT, topic=TOPIC, start_at=START_AT, end_at=END_AT)

    #user_ids = [row["user_id"] for row in results]
    screen_names = [row["user_screen_name"] for row in results]

    print(sorted(screen_names))

    # TODO: construct a graph using the psycopg grapher
