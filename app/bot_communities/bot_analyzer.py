import os

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.bot_communities.tokenizers import Tokenizer, SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies

from pandas import DataFrame

if __name__ == "__main__":

    tokenizer = Tokenizer()

    bq_service = BigQueryService()

    sql = f"""
    SELECT
        c.community_id
        ,b.bot_id
        -- ,b.bot_screen_name
        --,b.day_count
        --,b.avg_daily_score
        ,count(distinct t.status_id) as tweet_count
        ,STRING_AGG(DISTINCT upper(t.user_screen_name), ' | ') as screen_names
        ,STRING_AGG(DISTINCT upper(t.user_name), ' | ') as user_names
        ,STRING_AGG(DISTINCT upper(t.user_description), ' | ') as user_descriptions
    FROM impeachment_production.bots_above_80 b
    JOIN impeachment_production.2_bot_communities c ON c.user_id = b.bot_id
    JOIN impeachment_production.tweets t on cast(t.user_id as int64) = b.bot_id
    GROUP BY 1,2
    ORDER BY 1,2
    """ # TODO: move me into the BQ service

    results = [dict(row) for row in list(bq_service.execute_query(sql))]

    #descriptions = [row["user_descriptions"] for row in results]

    for i, row in enumerate(results):
        row["profile_tags"] = []
        row["profile_tokens"] = []

        if row["user_descriptions"]:
            print("--------------")
            print("COMMUNITY", row["community_id"], i, row["bot_id"], row["screen_names"])
            print(row["user_descriptions"])

            tags = list(set(tokenizer.hashtags(row["user_descriptions"])))
            print("TAGS:", tags)
            row["profile_tags"] = tags

            tokens = list(set(tokenizer.custom_stems(row["user_descriptions"])))
            row["profile_tokens"] = tokens

    df = DataFrame(results)
    csv_filepath = os.path.join(DATA_DIR,"bot_retweet_graphs", "bot_min", str(0.8), "n_communities", str(2), "bot_profiles.csv")
    df.to_csv(csv_filepath)


    breakpoint()
    top_tokens_df = summarize_token_frequencies(df["profile_tokens"].tolist())
