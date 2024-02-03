
import os

from pandas import read_csv, crosstab

from app import DATA_DIR

if __name__ == "__main__":

    csv_filepath = os.path.join(DATA_DIR, "hashtag_networks", "user_profile_hashtag_pairs_v4.csv")

    user_pairs_df = read_csv(csv_filepath)

    co_matrix = crosstab(user_pairs_df.tag_0, user_pairs_df.tag_1)

    breakpoint()
