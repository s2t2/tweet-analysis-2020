from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", default="postgresql://username:password@localhost/dbname")

class Pipeline():
    def __init__(self, database_url=DATABASE_URL):
        self.database_url = database_url
        self.db = create_engine(database_url)

if __name__ == "__main__":

    pipeline = Pipeline()

    # get user_friends from BQ

    # store into PG in batches

    print(pipeline.database_url)

    breakpoint()
