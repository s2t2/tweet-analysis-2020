

from app.bq_service import BigQueryService

LIMIT = 100 # None  # os.getenv("LIMIT")

def tweet_stream(limit=LIMIT):
    bq_service = BigQueryService()
    return bq_service.fetch_tag_tweets(limit=limit)

if __name__ == "__main__":
    print("HELLO")

    tweets = []
    for tweet in tweet_stream():
        print(tweet)
        tweets.append(tweet)

    print(len(tweets))
