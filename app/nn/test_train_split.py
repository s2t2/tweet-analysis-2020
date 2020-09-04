

from pandas import DataFrame
from sklearn.model_selection import train_test_split

from app import DATA_DIR
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService


if __name__ == "__main__":

    bq_service = BigQueryService()

    print("--------------------------")
    tweets = []
    for row in bq_service.fetch_labeled_tweets_in_batches():
        tweets.append(dict(row))
    print("LABELED TWEETS:", fmt_n(len(tweets)))

    tweets_df = DataFrame(tweets)
    print(tweets_df.head())

    stratify = tweets_df["community_id"] # population[['income', 'sex', 'age']]
    train_df, test_df = train_test_split(tweets_df, stratify=stratify, test_size=0.2, random_state=99)
    print("TEST/TRAIN SPLIT:", fmt_n(len(train_df)), fmt_n(len(test_df)))
    del test_df # we don't want to see you no mo!

    print("--------------------------")
    print("TRAINING DATA...")
    print(train_df.head())
    print(train_df["community_id"].value_counts()) # should be equal for each class!
    #raise ValueError("EXPECTING EQUAL NUMBER OF DATAPOINTS IN EACH COMMUNITY") unless both are the same
    breakpoint()

    #print("TRAIN/EVAL SPLIT:")
