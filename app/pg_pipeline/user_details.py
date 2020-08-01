

from app.pg_pipeline import Pipeline

if __name__ == "__main__":

    pipeline = Pipeline()

    pipeline.download_user_details() # takes about 50 minutes for 3.6M users in batches of 2500

    pipeline.report()

    pipeline.sleep()
