
import os
from functools import lru_cache

from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt, s_to_date
from app.decorators.number_decorators import fmt_n
from app.bot_communities.spectral_clustermaker import SpectralClustermaker
from app.bot_communities.tokenizers import Tokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies, train_topic_model, parse_topics, LdaMulticore

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

        self.retweets_dirpath = os.path.join(self.local_dirpath, "retweets")
        if not os.path.exists(self.retweets_dirpath):
            os.makedirs(self.retweets_dirpath)

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


class CommunityRetweetsAnalyzer:
    def __init__(self, community_id, community_retweets_df, local_dirpath, tokenize=None):
        self.community_id = community_id
        self.community_retweets_df = community_retweets_df
        self.local_dirpath = local_dirpath
        self.tokenize = tokenize or Tokenizer().custom_stems # todo: see if we can use a spacy version

    @property
    @lru_cache(maxsize=None)
    def most_retweets_df(self):
        print("USERS WITH MOST RETWEETS")
        df = self.community_retweets_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
        # fix / un-nest column names after the group:
        df.columns = list(map(" ".join, df.columns.values))
        df = df.reset_index()
        df.rename(columns={"status_id nunique": "Retweet Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
        return df

    def generate_most_retweets_chart(self, top_n=10):
        chart_df = self.most_retweets_df.copy()
        chart_df.sort_values("Retweet Count", ascending=False, inplace=True) # sort for top
        chart_df = chart_df[:top_n] # take top n rows

        chart_df.sort_values("Retweet Count", ascending=True, inplace=True) # re-sort for chart
        fig = px.bar(chart_df,
            x="Retweet Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users Most Retweeted by Bot Community {self.community_id}"
        )
        if APP_ENV == "development":
            fig.show()
        fig.write_image(os.path.join(self.local_dirpath, "most-retweets.png"))

    @property
    @lru_cache(maxsize=None)
    def most_retweeters_df(self):
        print("USERS WITH MOST RETWEETERS")
        df = self.community_retweets_df.groupby("retweeted_user_screen_name").agg({"user_id": ["nunique"]})
        df.columns = list(map(" ".join, df.columns.values))
        df = df.reset_index()
        df.rename(columns={"user_id nunique": "Retweeter Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
        return df

    def generate_most_retweeters_chart(self, top_n=10):
        chart_df = self.most_retweeters_df.copy()
        chart_df.sort_values("Retweeter Count", ascending=False, inplace=True) # sort for top
        most_retweeters_df = most_retweeters_df[:top_n]

        most_retweeters_df.sort_values("Retweeter Count", ascending=True, inplace=True) # re-sort for chart
        fig = px.bar(most_retweeters_df,
            x="Retweeter Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users with Most Retweeters in Bot Community {community_id} (n_communities={self.n_clusters})"
        )
        if APP_ENV == "development":
            fig.show()
        fig.write_image(os.path.join(self.local_dirpath, "most-retweeters.png"))

    #
    # NLP
    #

    @property
    @lru_cache(maxsize=None)
    def status_tokens(self):
        """Returns pandas.core.series.Series of statuses converted to tokens"""
        print("TOKENIZING...")
        return self.community_retweets_df["status_text"].apply(self.tokenize)

    @property
    @lru_cache(maxsize=None)
    def top_tokens_df(self):
        return summarize_token_frequencies(self.status_tokens.values.tolist())

    def save_top_tokens(self):
        self.top_tokens_df.to_csv(os.path.join(self.local_dirpath, "top-tokens.csv"))

    def generate_top_tokens_wordcloud(self, top_n=20):
        print("TOP TOKENS WORD CLOUD...")
        chart_df = self.top_tokens_df[self.top_tokens_df["rank"] <= top_n]

        squarify.plot(sizes=chart_df["pct"], label=chart_df["token"], alpha=0.8)
        plt.title(f"Word Cloud for Community {self.community_id} (n={fmt_n(len(self.community_retweets_df))})")
        plt.axis("off")
        if APP_ENV == "development":
            plt.show()
        plt.savefig(os.path.join(self.local_dirpath, "top-tokens-wordcloud.png"))
        plt.clf()  # clear the figure, to prevent topics from overlapping from previous plots

    #
    # TOPIC MODELING
    #

    @property
    @lru_cache(maxsize=None)
    def topic_model(self):
        ## if local file exists, load and return it, otherwise train a new one, save it and return it
        #if os.path.isfile(local_lda_path):
        #    lda = LdaModel.load(local_lda_path)
        #else:
        #    lda = train_topic_model(self.status_tokens.values.tolist())
        #    lda.save(local_lda_path)
        #return lda
        return train_topic_model(self.status_tokens.values.tolist())

    @property
    @lru_cache(maxsize=None)
    def topics_df(self):
        topics = parse_topics(self.topic_model)
        breakpoint()
        return DataFrame(topics)

    def save_topics(self):
        self.topics_df.to_csv(os.path.join(self.local_dirpath, "topics.csv"))


if __name__ == "__main__":

    analyzer = RetweetAnalyzer()
    analyzer.load_retweets()
    print(analyzer.retweets_df.head())

    seek_confirmation()

    for community_id in analyzer.community_ids:
        community_analyzer = CommunityRetweetsAnalyzer(
            community_id=community_id,
            community_retweets_df=analyzer.retweets_df[analyzer.retweets_df["community_id"] == community_id],
            local_dirpath=os.path.join(analyzer.local_dirpath, f"community-{community_id}")
        )

        print(logstamp(), community_id, "CHARTS...")
        community_analyzer.generate_most_retweets_chart()
        community_analyzer.generate_most_retweeters_chart()

        print(logstamp(), community_id, "TOKENS...")
        community_analyzer.top_tokens_df
        community_analyzer.save_top_tokens()
        community_analyzer.generate_top_tokens_wordcloud()

        print(logstamp(), community_id, "TOPICS...")
        #community_analyzer.topics_df # TODO: taking too long
        #community_analyzer.save_topics() # TODO: taking too long
