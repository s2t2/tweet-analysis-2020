
import os

from pandas import DataFrame, read_csv

from app.decorators.datetime_decorators import dt_to_s, logstamp
from app.decorators.number_decorators import fmt_n

from app.bot_communities.spectral_clustermaker import SpectralClustermaker

BATCH_SIZE = 50_000 # we are talking about downloading millions of records
#ROWS_LIMIT = os.getenv("ROWS_LIMIT")

class LocalStorage:
    def __init__(self):
        self.clustermaker = SpectralClustermaker()
        self.n_clusters = self.clustermaker.n_clusters
        self.bq_service = self.clustermaker.grapher.bq_service
        self.local_dirpath = self.clustermaker.local_dirpath

        #self.tweets_filepath = os.path.join(self.local_dirpath, "tweets.csv")
        self.retweets_filepath = os.path.join(self.local_dirpath, "retweets.csv")

        self.retweets_dirpath = os.path.join(self.local_dirpath, "retweets")
        if not os.path.exists(self.retweets_dirpath):
            os.makedirs(self.retweets_dirpath)

        self.retweets_df = None

    def load_retweets(self):
        """
        Loads or downloads bot community tweets to/from CSV.
        """
        if os.path.isfile(self.retweets_filepath):
            print("READING BOT COMMUNITY RETWEETS FROM CSV...")
            self.retweets_df = read_csv(self.retweets_filepath) # DtypeWarning: Columns (6) have mixed types.Specify dtype option on import or set low_memory=False
            #if ROWS_LIMIT:
            #    self.retweets_df = read_csv(local_csv_filepath, nrows=int(ROWS_LIMIT))
            #else:
            #    self.retweets_df = read_csv(local_csv_filepath)
        else:
            print("DOWNLOADING BOT COMMUNITY RETWEETS...")
            counter = 0
            records = []
            for row in self.bq_service.download_n_bot_community_retweets_in_batches(self.n_clusters):
                records.append({
                    "community_id": row.community_id,
                    "user_id": row.user_id,
                    "user_screen_name_count": row.user_screen_name_count,
                    "user_screen_names": row.user_screen_names,
                    "user_created_at": dt_to_s(row.user_created_at),

                    "retweeted_user_id": row.retweeted_user_id,
                    "retweeted_user_screen_name": row.retweeted_user_screen_name,

                    "status_id": row.status_id,
                    "status_text": row.status_text,
                    "status_created_at": dt_to_s(row.status_created_at)
                })
                counter+=1
                if counter % BATCH_SIZE == 0: print(logstamp(), fmt_n(counter))

            self.retweets_df = DataFrame(records)
            self.retweets_df.index.name = "row_id"
            self.retweets_df.index += 1
            print("WRITING TO FILE...")
            self.retweets_df.to_csv(self.retweets_filepath)

    @property
    def retweet_community_ids(self):
        if self.retweets_df is None:
            self.load_retweets()

        return list(self.retweets_df["community_id"].unique())
