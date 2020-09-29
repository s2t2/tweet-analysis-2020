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
    tokenizer = Tokenizer()

    results = []
    # TODO: consider doing a query per community, to reduce memory costs
    for row in bq_service.fetch_bot_community_tweets(n_communities=2):
        row = dict(row)
        row["status_tokens"] = []
        row["status_tags"] = []
        if row["status_text"]:
            row["status_tokens"] = tokenizer.custom_stems(row["status_text"])
            row["profile_tags"] = tokenizer.hashtags(row["status_text"])

    print("--------------")
    print("BOT STATUSES:")
    statuses_df = DataFrame(results)
    print(statuses_df.head())
    # SAVE AND UPLOAD TWEETS
    local_tweets_filepath = os.path.join(file_storage.local_dirpath, "community_tweets.csv")
    #gcs_tweets_filepath = os.path.join(file_storage.gcs_dirpath, "community_tweets.csv")
    statuses_df.to_csv(local_tweets_filepath)
    #file_storage.upload_file(local_tweets_filepath, gcs_tweets_filepath)

    for community_id, filtered_df in statuses_df.groupby(["community_id"]):
        print("--------------")
        print(f"COMMUNITY {community_id}:", len(filtered_df))
        local_community_dirpath = os.path.join(file_storage.local_dirpath, f"community_{community_id}")
        gcs_community_dirpath = os.path.join(file_storage.gcs_dirpath, f"community_{community_id}")
        if not os.path.exists(local_community_dirpath):
            os.makedirs(local_community_dirpath)

        tokens_df = summarize_token_frequencies(filtered_df["status_tokens"].tolist())
        print(tokens_df.head())
        # SAVE AND UPLOAD TOP TOKENS
        local_tokens_filepath = os.path.join(local_community_dirpath, "status_tokens.csv")
        gcs_tokens_filepath = os.path.join(gcs_community_dirpath, "status_tokens.csv")
        tokens_df.to_csv(local_tokens_filepath)
        file_storage.upload_file(local_tokens_filepath, gcs_tokens_filepath)
        token_records = tokens_df[tokens_df["count"] > 1].to_dict("records")[0:1000]
        bq_service.upload_bot_community_status_tokens(community_id=community_id, records=token_records)

        tags_df = summarize_token_frequencies(filtered_df["status_tags"].tolist())
        print(tags_df.head())
        # SAVE AND UPLOAD TOP TAGS
        local_tags_filepath = os.path.join(local_community_dirpath, "profile_tags.csv")
        gcs_tags_filepath = os.path.join(gcs_community_dirpath, "profile_tags.csv")
        tags_df.to_csv(local_tags_filepath)
        file_storage.upload_file(local_tags_filepath, gcs_tags_filepath)
        tag_records = tags_df[tags_df["count"] > 1].to_dict("records")[0:1000]
        bq_service.upload_bot_community_status_tags(community_id=community_id, records=tag_records)
