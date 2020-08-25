
import os

from pandas import DataFrame, read_csv

from app.decorators.datetime_decorators import dt_to_s, logstamp
from app.decorators.number_decorators import fmt_n
from app.bot_communities.spectral_clustermaker import SpectralClustermaker

BATCH_SIZE = 50_000 # we are talking about downloading 1-2M tweets

class CommunityTweetAnalyzer:
    def __init__(self):
        self.clustermaker = SpectralClustermaker()
        self.n_clusters = self.clustermaker.n_clusters

        self.bq_service = self.clustermaker.grapher.bq_service

        self.tweets_filepath = os.path.join(self.clustermaker.local_dirpath, "tweets.csv")
        print(os.path.abspath(self.tweets_filepath))

    def load_tweets(self):
        """
        Loads or downloads bot community tweets to/from CSV.
        """

        if os.path.isfile(self.tweets_filepath):
            print("READING BOT COMMUNITY TWEETS FROM CSV...")
            self.tweets_df = read_csv(self.tweets_filepath) # DtypeWarning: Columns (6) have mixed types.Specify dtype option on import or set low_memory=False
        else:
            print("DOWNLOADING BOT COMMUNITY TWEETS...")
            counter = 0
            records = []
            for row in self.bq_service.download_n_bot_community_tweets_in_batches(self.n_clusters):
                records.append({
                    "community_id": row.community_id,

                    "user_id": row.user_id,
                    "user_name": row.user_name,
                    "user_screen_name": row.user_screen_name,
                    "user_description": row.user_description,
                    "user_location": row.user_location,
                    "user_verified": row.user_verified,
                    "user_created_at": dt_to_s(row.user_created_at),

                    "status_id": row.status_id,
                    "status_text": row.status_text,
                    "reply_user_id": row.reply_user_id,
                    "retweet_status_id": row.retweet_status_id,
                    "status_is_quote": row.status_is_quote,
                    "status_geo": row.status_geo,
                    "status_created_at": dt_to_s(row.status_created_at)
                })
                counter+=1
                if counter % BATCH_SIZE == 0: print(logstamp(), fmt_n(counter))

            self.tweets_df = DataFrame(records)
            self.tweets_df.index.name = "row_id"
            self.tweets_df.index = self.tweets_df.index + 1
            print("WRITING TO FILE...")
            self.tweets_df.to_csv(self.tweets_filepath)


if __name__ == "__main__":

    analyzer = CommunityTweetAnalyzer()

    analyzer.load_tweets()

    print(analyzer.tweets_df.head())
