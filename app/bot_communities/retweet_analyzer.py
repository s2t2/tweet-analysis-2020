
import os
from functools import lru_cache

from pandas import DataFrame
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.bot_communities.csv_storage import LocalStorage
from app.bot_communities.tokenizers import Tokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies, train_topic_model, parse_topics, LdaMulticore


class RetweetsAnalyzer:
    def __init__(self, community_id, community_retweets_df, local_dirpath, tokenize=None):
        self.community_id = community_id
        self.community_retweets_df = community_retweets_df
        self.local_dirpath = local_dirpath
        self.tokenize = tokenize or Tokenizer().custom_stems # todo: see if we can use a spacy version

        if not os.path.exists(self.local_dirpath):
            os.makedirs(self.local_dirpath)

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
        chart_df = chart_df[:top_n]

        chart_df.sort_values("Retweeter Count", ascending=True, inplace=True) # re-sort for chart
        fig = px.bar(chart_df,
            x="Retweeter Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users with Most Retweeters in Bot Community {community_id}"
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

    storage = LocalStorage()
    storage.load_retweets()
    print(storage.retweets_df.head())

    seek_confirmation()

    for community_id in storage.retweet_community_ids:
        community_analyzer = RetweetsAnalyzer(
            community_id=community_id,
            community_retweets_df=storage.retweets_df[storage.retweets_df["community_id"] == community_id],
            local_dirpath=os.path.join(storage.local_dirpath, f"community-{community_id}")
        )

        print("------------------------")
        print(logstamp(), "COMMUNITY", community_id, "CHARTS...")
        community_analyzer.generate_most_retweets_chart()
        community_analyzer.generate_most_retweeters_chart()

        print("------------------------")
        print(logstamp(), "COMMUNITY", community_id, "TOKENS...")
        community_analyzer.top_tokens_df
        community_analyzer.save_top_tokens()
        community_analyzer.generate_top_tokens_wordcloud()

        print("------------------------")
        print(logstamp(), "COMMUNITY", community_id, "TOPICS...")
        #community_analyzer.topics_df # TODO: taking too long
        #community_analyzer.save_topics() # TODO: taking too long
