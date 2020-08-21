
import os

from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.spectral_clustermaker import N_COMMUNITIES # TODO
from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt, s_to_date
from app.decorators.number_decorators import fmt_n
from app.bot_communities.token_maker import CustomTokenMaker

BATCH_SIZE = 50_000 # we are talking about downloading 1-2M tweets
RETWEET_BENEFICIARY_CHARTS = True
CREATION_DATES_CHART = False
TOKENIZE = True
TOKEN_CLOUD = True

class CommunityAnalyzer:
    def __init__(self):
        self.clustermaker = SpectralClustermaker()
        self.n_clusters = self.clustermaker.n_clusters

        self.bq_service = self.clustermaker.grapher.bq_service

        #self.tweets_filepath = os.path.join(self.clustermaker.local_dirpath, "tweets.csv")
        self.retweets_filepath = os.path.join(self.clustermaker.local_dirpath, "retweets.csv")

        self.retweet_charts_dirpath = os.path.join(local_dirpath, "retweet_charts")
        if not os.path.exists(self.retweet_charts_dirpath):
            os.makedirs(self.retweet_charts_dirpath)

    def load_retweets(self):
        """
        Loads or downloads bot community tweets to/from CSV.
        """

        if os.path.isfile(self.retweets_filepath):
            print("READING BOT COMMUNITY RETWEETS FROM CSV...")
            self.retweets_df = read_csv(self.retweets_filepath) # DtypeWarning: Columns (6) have mixed types.Specify dtype option on import or set low_memory=False
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
            self.retweets_df.index = self.retweets_df.index + 1
            print("WRITING TO FILE...")
            self.retweets_df.to_csv(self.retweets_filepath)


if __name__ == "__main__":

    analyzer = CommunityAnalyzer()

    analyzer.load_retweets()

    print(analyzer.retweets_df.head())

    seek_confirmation()

    #
    # ANALYZE DATA
    #

    token_maker = CustomTokenMaker()

    community_ids = list(df["community_id"].unique())
    for community_id in community_ids:
        print(logstamp(), community_id)

        community_df = df[df["community_id"] == community_id]

        if RETWEET_BENEFICIARY_CHARTS:
            print("-------------------------")
            print("USERS MOST RETWEETED")
            most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
            most_retweeted_df.columns = list(map(" ".join, most_retweeted_df.columns.values))
            most_retweeted_df = most_retweeted_df.reset_index()
            most_retweeted_df.rename(columns={"status_id nunique": "Retweet Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
            most_retweeted_df.sort_values("Retweet Count", ascending=False, inplace=True)
            most_retweeted_df = most_retweeted_df[:10]
            print(most_retweeted_df)

            most_retweeted_df.sort_values("Retweet Count", ascending=True, inplace=True)
            fig = px.bar(most_retweeted_df,
                x="Retweet Count",
                y="Retweeted User",
                orientation="h",
                title=f"Users Most Retweeted by Bot Community {community_id} (K Communities: {N_COMMUNITIES})"
            )
            if APP_ENV == "development":
                fig.show()

            local_img_filepath = os.path.join(charts_dirpath, f"community-{community_id}-most-retweeted.png")
            fig.write_image(local_img_filepath)

        if RETWEET_BENEFICIARY_CHARTS:
            print("-------------------------")
            print("USERS MOST RETWEETERS")
            most_retweeters_df = community_df.groupby("retweeted_user_screen_name").agg({"user_id": ["nunique"]})
            most_retweeters_df.columns = list(map(" ".join, most_retweeters_df.columns.values))
            most_retweeters_df = most_retweeters_df.reset_index()
            most_retweeters_df.rename(columns={"user_id nunique": "Retweeter Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
            most_retweeters_df.sort_values("Retweeter Count", ascending=False, inplace=True)
            most_retweeters_df = most_retweeters_df[:10]
            print(most_retweeters_df)

            most_retweeters_df.sort_values("Retweeter Count", ascending=True, inplace=True)
            fig_retweeters = px.bar(most_retweeters_df,
                x="Retweeter Count",
                y="Retweeted User",
                orientation="h",
                title=f"Users with Most Retweeters by Bot Community {community_id} (K Communities: {N_COMMUNITIES})"
            )
            if APP_ENV == "development":
                fig_retweeters.show()

            local_img_filepath = os.path.join(charts_dirpath, f"community-{community_id}-most-retweeters.png")
            fig_retweeters.write_image(local_img_filepath)

        if CREATION_DATES_CHART:
            pass
            #creation_dates_df = community_df.groupby("user_id").agg({"user_created_at": ["min"]})
            #creation_dates_df["user_created_at"]["min"] = creation_dates_df["user_created_at"]["min"].apply(dts_to_date)
            #print(creation_dates_df.head())

        if TOKENIZE:

            print("-------------------------")
            print("TOKENIZING (NOT THE BEST WAY, BUT THE WAY THAT WILL ACTUALLY COMPLETE GIVEN THE LARGE VOLUME)...")
            #status_tokens = community_df["status_text"].apply(lambda txt: token_maker.tokenize_custom_stems(txt))
            status_tokens = community_df["status_text"].apply(token_maker.tokenize_custom_stems)

            print("-------------------------")
            print("SUMMARIZING...")
            token_ranks_df = token_maker.summarize(status_tokens.values.tolist())

            print("-------------------------")
            print("SAVING TOKENS...")
            local_top_tokens_filepath = os.path.join(local_dirpath, f"community-{community_id}-top-tokens.csv")
            token_ranks_df.to_csv(local_top_tokens_filepath) # let's save them all, not just the top ones

            if TOKEN_CLOUD:
                print("-------------------------")
                print("GENERATING WORD CLOUD...")
                wordcloud_df = token_ranks_df[token_ranks_df["rank"] <= 20]
                chart_title = f"Word Cloud for Community {community_id} (n={fmt_n(len(community_df))})"
                squarify.plot(sizes=wordcloud_df["pct"], label=wordcloud_df["token"], alpha=0.8)
                plt.title(chart_title)
                plt.axis("off")
                if APP_ENV == "development":
                    plt.show()

                local_wordcloud_filepath = os.path.join(charts_dirpath, f"community-{community_id}-wordcloud.png")
                print(os.path.abspath(local_wordcloud_filepath))
                plt.savefig(local_wordcloud_filepath)

                plt.clf() # clear the figure, to prevent topics from overlapping from previous plots
