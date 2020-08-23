
import os

from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt, s_to_date
from app.decorators.number_decorators import fmt_n
from app.bot_communities.spectral_clustermaker import SpectralClustermaker
from app.bot_communities.tokenizers import Tokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies

BATCH_SIZE = 50_000 # we are talking about downloading millions of records
#ROWS_LIMIT = os.getenv("ROWS_LIMIT")

class RetweetAnalyzer:
    def __init__(self, tokenize=None):
        self.clustermaker = SpectralClustermaker()
        self.n_clusters = self.clustermaker.n_clusters
        self.bq_service = self.clustermaker.grapher.bq_service
        self.local_dirpath = self.clustermaker.local_dirpath

        #self.tweets_filepath = os.path.join(self.local_dirpath, "tweets.csv")
        self.retweets_filepath = os.path.join(self.local_dirpath, "retweets.csv")

        self.retweet_charts_dirpath = os.path.join(self.local_dirpath, "retweet_charts")
        if not os.path.exists(self.retweet_charts_dirpath):
            os.makedirs(self.retweet_charts_dirpath)

        self.tokenize = tokenize or Tokenizer().custom_stems # using the faster version, not the spacy version, due to time constraints

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
    def community_ids(self):
        return list(self.retweets_df["community_id"].unique())

    def generate_users_most_retweeted_chart(self, community_id, top_n=10):
        community_df = self.retweets_df[self.retweets_df["community_id"] == community_id]

        print("-------------------------")
        print("USERS MOST RETWEETED")
        most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
        most_retweeted_df.columns = list(map(" ".join, most_retweeted_df.columns.values))
        most_retweeted_df = most_retweeted_df.reset_index()
        most_retweeted_df.rename(columns={"status_id nunique": "Retweet Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)

        most_retweeted_df.sort_values("Retweet Count", ascending=False, inplace=True) # sort for top
        most_retweeted_df = most_retweeted_df[:top_n]
        print(most_retweeted_df)

        most_retweeted_df.sort_values("Retweet Count", ascending=True, inplace=True) # re-sort for charting
        fig = px.bar(most_retweeted_df,
            x="Retweet Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users Most Retweeted by Bot Community {community_id} (n_communities={self.n_clusters})"
        )
        if APP_ENV == "development":
            fig.show()

        local_img_filepath = os.path.join(self.retweet_charts_dirpath, f"most-retweeted-community-{community_id}.png")
        fig.write_image(local_img_filepath)

    def generate_users_most_retweeters_chart(self, community_id, top_n=10):
        community_df = self.retweets_df[self.retweets_df["community_id"] == community_id]

        print("-------------------------")
        print("USERS WITH MOST RETWEETERS")
        most_retweeters_df = community_df.groupby("retweeted_user_screen_name").agg({"user_id": ["nunique"]})
        most_retweeters_df.columns = list(map(" ".join, most_retweeters_df.columns.values))
        most_retweeters_df = most_retweeters_df.reset_index()
        most_retweeters_df.rename(columns={"user_id nunique": "Retweeter Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)

        most_retweeters_df.sort_values("Retweeter Count", ascending=False, inplace=True) # sort for top
        most_retweeters_df = most_retweeters_df[:top_n]
        print(most_retweeters_df)

        most_retweeters_df.sort_values("Retweeter Count", ascending=True, inplace=True) # re-sort for chart
        fig = px.bar(most_retweeters_df,
            x="Retweeter Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users with Most Retweeters in Bot Community {community_id} (n_communities={self.n_clusters})"
        )
        if APP_ENV == "development":
            fig.show()

        local_img_filepath = os.path.join(self.retweet_charts_dirpath, f"most-retweeters-community-{community_id}.png")
        fig.write_image(local_img_filepath)

    def generate_creation_dates_histogram(self, community_id):
        pass # TODO
        #creation_dates_df = community_df.groupby("user_id").agg({"user_created_at": ["min"]})
        #creation_dates_df["user_created_at"]["min"] = creation_dates_df["user_created_at"]["min"].apply(dts_to_date)
        #print(creation_dates_df.head())

    def generate_token_ranks_df(self, community_id):
        community_df = self.retweets_df[self.retweets_df["community_id"] == community_id]
        print("-------------------------")
        print("TOKENIZING...")
        status_tokens = community_df["status_text"].apply(self.tokenize)
        token_ranks_df = summarize_token_frequencies(status_tokens.values.tolist())

        csv_filepath = os.path.join(self.retweet_charts_dirpath, f"top-tokens-community-{community_id}.csv")
        token_ranks_df.to_csv(csv_filepath)  # let's save them all, not just the top ones
        return token_ranks_df

    def generate_wordcloud(self, community_id, token_ranks_df):
        community_df = self.retweets_df[self.retweets_df["community_id"] == community_id]
        print("-------------------------")
        print("GENERATING WORD CLOUD...")
        wordcloud_df = token_ranks_df[token_ranks_df["rank"] <= 20]
        chart_title = f"Word Cloud for Community {community_id} (n={fmt_n(len(community_df))})"
        squarify.plot(sizes=wordcloud_df["pct"], label=wordcloud_df["token"], alpha=0.8)
        plt.title(chart_title)
        plt.axis("off")
        if APP_ENV == "development":
            plt.show()

        img_filepath = os.path.join(self.retweet_charts_dirpath, f"wordcloud-community-{community_id}.png")
        print(os.path.abspath(img_filepath))
        plt.savefig(img_filepath)
        plt.clf()  # clear the figure, to prevent topics from overlapping from previous plots

if __name__ == "__main__":

    analyzer = RetweetAnalyzer()

    analyzer.load_retweets()
    print(analyzer.retweets_df.head())

    seek_confirmation()

    for community_id in analyzer.community_ids:
        print(logstamp(), community_id)

        analyzer.generate_users_most_retweeted_chart(community_id)

        analyzer.generate_users_most_retweeters_chart(community_id)

        # analyzer.generate_creation_dates_histogram(community_id)

        token_ranks_df = analyzer.generate_token_ranks_df(community_id)

        analyzer.generate_wordcloud(community_id, token_ranks_df)
