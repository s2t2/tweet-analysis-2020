import os

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.bot_communities.tokenizers import Tokenizer #, SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies

from pandas import DataFrame


if __name__ == "__main__":

    file_storage = FileStorage(dirpath="bot_retweet_graphs/bot_min/0.8/n_communities/2/analysis_v2")
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

    profiles_df = DataFrame(results)
    print(profiles_df.head())
    local_profiles_filepath = os.path.join(file_storage.local_dirpath, "community_profiles.csv")
    gcs_profiles_filepath = os.path.join(file_storage.gcs_dirpath, "community_profiles.csv")
    profiles_df.to_csv(local_profiles_filepath)
    file_storage.upload_file(local_profiles_filepath, gcs_profiles_filepath)

    #
    # SUMMARIZE BY COMMUNITY...
    #

    for community_id, filtered_df in profiles_df.groupby(["community_id"]):
        print("--------------")
        print("COMMUNITY", community_id, "-", len(filtered_df), "BOT PROFILES")
        local_community_dirpath = os.path.join(file_storage.local_dirpath, f"community_{community_id}")
        gcs_community_dirpath = os.path.join(file_storage.gcs_dirpath, f"community_{community_id}")
        os.makedirs(local_community_dirpath)

        tokens_df = summarize_token_frequencies(filtered_df["profile_tokens"].tolist())
        print(tokens_df.head())
        local_tokens_filepath = os.path.join(local_community_dirpath, "profile_tokens.csv")
        gcs_tokens_filepath = os.path.join(gcs_community_dirpath, "profile_tokens.csv")
        tokens_df.to_csv(local_tokens_filepath)
        file_storage.upload_file(local_tokens_filepath, gcs_tokens_filepath)

        tags_df = summarize_token_frequencies(filtered_df["profile_tags"].tolist())
        print(tags_df.head())
        local_tags_filepath = os.path.join(local_community_dirpath, "profile_tags.csv")
        gcs_tags_filepath = os.path.join(gcs_community_dirpath, "profile_tags.csv")
        tags_df.to_csv(local_tags_filepath)
        file_storage.upload_file(local_tags_filepath, gcs_tags_filepath)
