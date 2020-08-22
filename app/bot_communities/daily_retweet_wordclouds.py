import os

from pandas import read_csv, DataFrame

import matplotlib.pyplot as plt
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import s_to_date, logstamp #dt_to_s, logstamp, dt_to_date, s_to_dt
from app.decorators.number_decorators import fmt_n
from app.bot_communities.retweet_analyzer import RetweetAnalyzer
from app.bot_communities.tokenizers import SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies


if __name__ == "__main__":

    analyzer = RetweetAnalyzer()
    analyzer.load_retweets()
    df = analyzer.retweets_df
    print(df.head())

    seek_confirmation()

    tokenizer = SpacyTokenizer()
    tokenize = tokenizer.custom_stem_lemmas

    daily_wordclouds_dirpath = os.path.join(analyzer.local_dirpath, "daily_wordclouds")
    if not os.path.exists(daily_wordclouds_dirpath):
        os.makedirs(daily_wordclouds_dirpath)

    print("----------------")
    print("TRANSFORMING RETWEETS...")
    df["status_created_date"] = df["status_created_at"].apply(s_to_date)

    daily_top_tokens = []
    for group_name, filtered_df in df.groupby(["status_created_date", "community_id"]):
        date = group_name[0]
        community_id = group_name[1]
        print(logstamp(), date, community_id)

        # TODO: parallelize the following steps...
        status_tokens = filtered_df["status_text"].apply(tokenize)
        token_ranks_df = summarize_token_frequencies(status_tokens.values.tolist())

        print("SAVING TOP TOKENS...")
        records = token_ranks_df[token_ranks_df["rank"] <= 250].to_dict("records")
        for record in records:
            record["community_id"] = community_id
            record["date"] = date
        daily_top_tokens += records

        print("PLOTTING TOP TOKENS...")
        chart_df = token_ranks_df[token_ranks_df["rank"] <= 20]
        squarify.plot(sizes=chart_df["pct"], label=chart_df["token"], alpha=0.8)
        chart_title = f"Word Cloud for Community {community_id} on '{date}' (n={fmt_n(len(filtered_df))})"
        plt.title(chart_title)
        plt.axis("off")
        if APP_ENV == "development":
            plt.show()
        img_filepath = os.path.join(daily_wordclouds_dirpath, f"community-{community_id}-{date}.png")
        print(os.path.abspath(img_filepath))
        plt.savefig(img_filepath)
        plt.clf() # clear the figure, to prevent topics from overlapping from previous plots

        seek_confirmation()

    try:
        daily_top_tokens_df = DataFrame(daily_top_tokens)
        daily_top_tokens_filepath = os.path.join(analyzer.local_dirpath, "daily_top_tokens.csv")
        daily_top_tokens_df.to_csv(daily_top_tokens_filepath)
    except:
        breakpoint()
