
import os
from collections import Counter

from pandas import read_csv

from app import DATA_DIR
from app.bq_service import BigQueryService

LIMIT = 100_000

if __name__ == "__main__":

    local_dirpath = os.path.join(DATA_DIR, "nn", "n_communities", str(2))
    os.makedirs(local_dirpath) # should already be there

    tags_csv_filepath = os.path.join(local_dirpath, "community_tags.csv") # should already be there
    tags_df = read_csv(tags_csv_filepath)
    blue_tags = tags_df[tags_df["community_id"] == 0]["hashtag"].tolist()
    red_tags = tags_df[tags_df["community_id"] == 1]["hashtag"].tolist()

    bq_service = BigQueryService()

    ##results = []
    ##for row in bq_service.fetch_user_details_v3_in_batches(limit=LIMIT):
    ##    user_names = " | ".join(row["user_names"])
    ##    descriptions = " | ".join(row["descriptions"])
    ##    #results.append(dict(row))
    ##    for red_tag in red_tags:
    ##    results.append({**dict(row), **{"red_score": red_score, "blue_score:" blue_score}})

    red_counter = Counter()
    for red_tag in red_tags:
        # get all users with that tag in their name or description
        # count their user_ids
        matching_users = bq_service.fetch_users_by_profile_tag(red_tag)
        breakpoint()
        token_counter.update(tokens)






WHEN '#RESIST'
WHEN '#THERESISTANCE'
WHEN '#RESISTANCE'
WHEN '#FBR'
WHEN '#VOTEBLUENOMATTERWHO'
WHEN '#VOTEBLUE'
WHEN '#BLUEWAVE2020'
WHEN '#IMPEACHTRUMP'
WHEN '#BIDEN2020'
WHEN '#IMPEACHTRUMPNOW'
WHEN '#METOO'
WHEN '#IMPEACH'
WHEN '#BLUEWAVE'
WHEN '#VOTEBLUE2020'
WHEN '#WTP2020'
WHEN '#BLM'
WHEN '#IMPEACHANDREMOVE'
WHEN '#RESISTER'
WHEN '#IMPOTUS'
WHEN '#NOTMYPRESIDENT'
WHEN '#DEMCAST
