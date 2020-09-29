import os

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.bot_communities.tokenizers import Tokenizer, SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies

from pandas import DataFrame

if __name__ == "__main__":

    local_dirpath = os.path.join(DATA_DIR,"bot_retweet_graphs", "bot_min", str(0.8), "n_communities", str(2))

    tokenizer = Tokenizer()
    spacy_tokenizer = SpacyTokenizer()

    bq_service = BigQueryService()

    sql = f"""
        SELECT
            c.community_id
            ,b.bot_id
            -- ,b.bot_screen_name
            --,b.day_count
            --,b.avg_daily_score
            ,count(distinct t.status_id) as tweet_count
            ,COALESCE(STRING_AGG(DISTINCT upper(t.user_screen_name), ' | ') , "")   as screen_names
            ,COALESCE(STRING_AGG(DISTINCT upper(t.user_name), ' | ')        , "")   as user_names
            ,COALESCE(STRING_AGG(DISTINCT upper(t.user_description), ' | ') , "")   as user_descriptions
        FROM impeachment_production.bots_above_80 b
        JOIN impeachment_production.2_bot_communities c ON c.user_id = b.bot_id
        JOIN impeachment_production.tweets t on cast(t.user_id as int64) = b.bot_id
        GROUP BY 1,2
        ORDER BY 1,2
    """ # TODO: move me into the BQ service

    results = [dict(row) for row in list(bq_service.execute_query(sql))]
    print("PROCESSING", len(results), "RECORDS...")

    for i, row in enumerate(results):
        row["profile_tokens"] = []
        row["profile_lemmas"] = []
        row["profile_tags"] = []
        row["profile_handles"] = []

        if row["user_descriptions"]:
            #print("--------------")
            #print("COMMUNITY", row["community_id"], i, row["bot_id"], row["screen_names"])
            #print(row["user_descriptions"])

            # we want unique tokens here because otherwise someone changing their sn will have a greater influence over the counts
            tokens = list(set(tokenizer.custom_stems(row["user_descriptions"])))
            row["profile_tokens"] = tokens
            #print("TOKENS:", tokens)

            lemmas = list(set(spacy_tokenizer.custom_stem_lemmas(row["user_descriptions"])))
            row["profile_lemmas"] = lemmas
            #print("LEMMAS:", lemmas)

            tags = list(set(tokenizer.hashtags(row["user_descriptions"])))
            row["profile_tags"] = tags
            #print("TAGS:", tags)

            handles = list(set(tokenizer.handles(row["user_descriptions"])))
            row["profile_handles"] = handles
            #print("HANDLES:", handles)

            # these are interesting...
            #ents = list(set([ent.text for ent in spacy_tokenizer.entity_tokens(row["user_descriptions"])]))
            #row["ents"] = ents
            #print("ENTITIES:", ents)

    df = DataFrame(results)
    df.to_csv(os.path.join(local_dirpath, "bot_profiles.csv"))
    print(df.head())

    #
    # SUMMARIZE BY COMMUNITY...
    #

    for community_id, filtered_df in df.groupby(["community_id"]):
        print("--------------")
        print("COMMUNITY", community_id, "-", len(filtered_df), "BOTS")

        top_tokens_df = summarize_token_frequencies(filtered_df["profile_tokens"].tolist())
        top_lemmas_df = summarize_token_frequencies(filtered_df["profile_lemmas"].tolist())
        top_tags_df = summarize_token_frequencies(filtered_df["profile_tags"].tolist())
        top_handles_df = summarize_token_frequencies(filtered_df["profile_handles"].tolist())

        print(top_tokens_df.head())
        print(top_lemmas_df.head())
        print(top_tags_df.head())
        print(top_handles_df.head())

        community_dirpath = os.path.join(local_dirpath, f"community-{community_id}")
        top_tokens_df.to_csv(os.path.join(community_dirpath, "top_profile_tokens.csv"))
        top_lemmas_df.to_csv(os.path.join(community_dirpath, "top_profile_lemmas.csv"))
        top_tags_df.to_csv(os.path.join(community_dirpath, "top_profile_tags.csv"))
        top_handles_df.to_csv(os.path.join(community_dirpath, "top_profile_handles.csv"))
