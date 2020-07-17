

from app.workers.pg_pipeline import Pipeline

if __name__ == "__main__":

    pipeline = Pipeline()

    pipeline.download_retweeter_details() # takes about __ minutes for 2.7M users in batches of 2500

    pipeline.report()
