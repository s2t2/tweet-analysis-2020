import os

from app import DATA_DIR
from app.bq_service import BigQueryService
#from app.file_storage import FileStorage
from app.bot_communities.tokenizers import Tokenizer #, SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies

from pandas import DataFrame

if __name__ == "__main__":

    local_dirpath = os.path.join(DATA_DIR, "bot_retweet_graphs", "bot_min", str(0.8), "n_communities", str(2))
    profiles_filepath = os.path.join(local_dirpath, "tokenized_profiles.csv")

    bq_service = BigQueryService()
    results = [dict(row) for row in list(bq_service.fetch_bot_community_profiles(n_communities=2))]
    print("PROCESSING", len(results), "RECORDS...")

    tokenizer = Tokenizer()
    for i, row in enumerate(results):
        row["profile_tokens"] = []
        row["profile_tags"] = []

        if row["user_descriptions"]:
            #print("--------------")
            #print("COMMUNITY", row["community_id"], i, row["bot_id"], row["screen_names"])
            #print(row["user_descriptions"])

            # we want unique tokens here because otherwise someone changing their sn will have a greater influence over the counts
            tokens = list(set(tokenizer.custom_stems(row["user_descriptions"])))
            row["profile_tokens"] = tokens
            #print("TOKENS:", tokens)

            tags = list(set(tokenizer.hashtags(row["user_descriptions"])))
            row["profile_tags"] = tags
            #print("TAGS:", tags)

    df = DataFrame(results)
    df.to_csv(profiles_filepath)
    print(df.head())

    #
    # SUMMARIZE BY COMMUNITY...
    #

    for community_id, filtered_df in df.groupby(["community_id"]):
        print("--------------")
        print("COMMUNITY", community_id, "-", len(filtered_df), "BOT PROFILES")
        community_dirpath = os.path.join(local_dirpath, f"community-{community_id}")
        top_tokens_filepath = os.path.join(community_dirpath, "top_profile_tokens.csv")
        top_tags_filepath = os.path.join(community_dirpath, "top_profile_tags.csv")

        top_tokens_df = summarize_token_frequencies(filtered_df["profile_tokens"].tolist())
        print(top_tokens_df.head())
        top_tokens_df.to_csv(top_tokens_filepath)

        top_tags_df = summarize_token_frequencies(filtered_df["profile_tags"].tolist())
        print(top_tags_df.head())
        top_tags_df.to_csv(top_tags_filepath)
