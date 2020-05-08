
import time
import os
from dotenv import load_dotenv
from app.models import db, UserFriend, BoundSession
from app.storage_service import BigQueryService, generate_timestamp, bigquery

load_dotenv()

BATCH_SIZE = os.getenv("BATCH_SIZE", default=100)

class AnalysisPipeline():
    def __init__(self, batch_size=BATCH_SIZE, bq=None):
        self.bq = (bq or BigQueryService.cautiously_initialized())
        self.db = db
        self.session = BoundSession()
        self.batch_size = batch_size
        self.batch = []
        self.counter = 0

    def perform(self):
        self.start_at = time.perf_counter()
        for row in self.bq.fetch_user_friends_in_batches():
            self.batch.append(row)
            self.counter+=1
            if self.counter % self.batch_size == 0:
                print(generate_timestamp(), self.counter)

                # todo: store users in database

                breakpoint()
                #user_friends.insert().values([
                #    {"name": "some name"},
                #    {"name": "some other name"},
                #    {"name": "yet another name"},
                #])
                session.bulk_insert_mappings(UserFriend, self.batch)
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

if __name__ == "__main__":

    if not UserFriend.__table__.exists():
        UserFriend.__table__.create(db)

    pipeline = AnalysisPipeline()
    pipeline.perform()
    pipeline.report()











    session.close()
