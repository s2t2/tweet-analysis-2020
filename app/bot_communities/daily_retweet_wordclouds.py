import os

from dotenv import load_dotenv
from pandas import read_csv, DataFrame

import matplotlib.pyplot as plt
import squarify
#import plotly.express as px

from app import APP_ENV, seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.spectral_clustermaker import N_COMMUNITIES # TODO
from app.bot_communities.token_maker import CustomTokenMaker
from app.decorators.datetime_decorators import s_to_date, logstamp #dt_to_s, logstamp, dt_to_date, s_to_dt
from app.decorators.number_decorators import fmt_n

load_dotenv()

ROWS_LIMIT = os.getenv("ROWS_LIMIT")

#class RetweetAnalyzer(object):
#    def load_or_download(self):
#        pass

if __name__ == "__main__":

    print("----------------")
    print("K COMMUNITIES:", N_COMMUNITIES)

    grapher = BotRetweetGrapher()
    local_dirpath = os.path.join(grapher.local_dirpath, "n_communities", str(N_COMMUNITIES)) # dir should be already made by cluster maker
    if not os.path.exists(local_dirpath):
        os.makedirs(local_dirpath)
    daily_wordclouds_dirpath = os.path.join(local_dirpath, "daily_wordclouds")
    if not os.path.exists(daily_wordclouds_dirpath):
        os.makedirs(daily_wordclouds_dirpath)

    print("----------------")
    print("LOADING RETWEETS...")
    local_csv_filepath = os.path.join(local_dirpath, "retweets.csv")
    print(os.path.abspath(local_csv_filepath))
    if ROWS_LIMIT:
        df = read_csv(local_csv_filepath, nrows=int(ROWS_LIMIT))
    else:
        df = read_csv(local_csv_filepath)
    print(df.head())

    print("----------------")
    print("TRANSFORMING RETWEETS...")
    df["status_created_date"] = df["status_created_at"].apply(s_to_date)


    daily_top_tokens = [] # for each token, add dates and ranks
    token_maker = CustomTokenMaker()

    for group_name, filtered_df in df.groupby(["status_created_date", "community_id"]):
        date = group_name[0]
        community_id = group_name[1]
        print(logstamp(), date, community_id)

        #status_tokens = filtered_df["status_text"].apply(lambda txt: tokenize_spacy_lemmas(txt))
        status_tokens = filtered_df["status_text"].apply(token_maker.tokenize)
        print(status_tokens)
        status_tokens = status_tokens.values.tolist()
        print("TOP TOKENS:")
        token_ranks_df = token_maker.summarize(status_tokens)

        if True:
            print("SAVING TOP TOKENS...")
            records = token_ranks_df[token_ranks_df["rank"] <= 250].to_dict("records")
            for record in records:
                record["community_id"] = community_id
                record["date"] = date
            daily_top_tokens += records

        if True:
            print("PLOTTING TOP TOKENS...")
            top_tokens_df = token_ranks_df[token_ranks_df["rank"] <= 20]
            squarify.plot(sizes=top_tokens_df["pct"], label=top_tokens_df["token"], alpha=0.8)
            chart_title = f"Word Cloud for Community {community_id} on '{date}' (n={fmt_n(len(filtered_df))})"
            plt.title(chart_title)
            plt.axis("off")
            if APP_ENV == "development":
                plt.show()
            local_wordcloud_filepath = os.path.join(daily_wordclouds_dirpath, f"community-{community_id}-{date}.png")
            print(os.path.abspath(local_wordcloud_filepath))
            plt.savefig(local_wordcloud_filepath)
            plt.clf() # clear the figure, to prevent topics from overlapping from previous plots

        seek_confirmation()

    daily_top_tokens_df = DataFrame(daily_top_tokens)
    daily_top_tokens_filepath = os.path.join(local_dirpath, "daily_top_tokens.csv")
    daily_top_tokens_df.to_csv(daily_top_tokens_filepath)
