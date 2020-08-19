
import os

from pandas import DataFrame, read_csv

from app import APP_ENV, seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.clustering import K_COMMUNITIES
from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt
from app.decorators.number_decorators import fmt_n

BATCH_SIZE = 50_000 # we are talking about downloading 1-2M tweets

if __name__ == "__main__":

    print("----------------")
    print("K COMMUNITIES:", K_COMMUNITIES)

    grapher = BotRetweetGrapher()
    local_dirpath = os.path.join(grapher.local_dirpath, "k_communities", str(K_COMMUNITIES)) # dir should be already made by cluster maker
    local_csv_filepath = os.path.join(local_dirpath, "tweets.csv")
    print(os.path.abspath(local_csv_filepath))
    if not os.path.exists(local_dirpath):
        os.makedirs(local_dirpath)

    #
    # LOAD DATA
    #

    if os.path.isfile(local_csv_filepath):
        print("LOADING BOT COMMUNITY TWEETS...")
        df = read_csv(local_csv_filepath)
    else:
        print("DOWNLOADING BOT COMMUNITY TWEETS...")
        sql = f"""

            SELECT
                bc.community_id

                ,t.user_id
                ,t.user_name
                ,t.user_screen_name
                ,t.user_description
                ,t.user_location
                ,t.user_verified
                ,t.user_created_at

                ,t.status_id
                ,t.status_text
                ,t.retweet_status_id
                ,t.reply_user_id
                ,t.is_quote as status_is_quote
                ,t.geo as status_geo
                ,t.created_at as status_created_at

            FROM `{grapher.bq_service.dataset_address}.{K_COMMUNITIES}_bot_communities` bc -- 681
            JOIN `{grapher.bq_service.dataset_address}.tweets` t on CAST(t.user_id as int64) = bc.user_id
            -- WHERE t.retweet_status_id IS NULL
            -- ORDER BY 1,2

        """
        counter = 0
        records = []
        for row in grapher.bq_service.execute_query_in_batches(sql):
            records.append({
                "community_id": row.community_id,

                "user_id": row.user_id,
                "user_name": row.user_name,
                "user_screen_name": row.user_screen_name,
                "user_description": row.user_description,
                "user_location": row.user_location,
                "user_verified": row.user_verified,
                "user_created_at": dt_to_s(row.user_created_at),

                "status_id": row.status_id,
                "status_text": row.status_text,
                "reply_user_id": row.reply_user_id,
                "retweet_status_id": row.retweet_status_id,
                "status_is_quote": row.status_is_quote,
                "status_geo": row.status_geo,
                "status_created_at": dt_to_s(row.status_created_at)
            })
            counter+=1
            if counter % BATCH_SIZE == 0:
                print(logstamp(), fmt_n(counter))

        df = DataFrame(records)
        print(df.head())
        print("WRITING TO FILE...")
        df.to_csv(local_csv_filepath)
