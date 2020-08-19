
import os

from pandas import DataFrame, read_csv
import matplotlib as plt
import plotly.express as px

from app import APP_ENV, seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.clustering import K_COMMUNITIES
from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt
from app.decorators.number_decorators import fmt_n

BATCH_SIZE = 50_000 # we are talking about downloading 1-2M tweets

def date_string_conversion(dtstr):
    return dt_to_date(s_to_dt(dtstr))

if __name__ == "__main__":

    print("----------------")
    print("K COMMUNITIES:", K_COMMUNITIES)

    grapher = BotRetweetGrapher()
    local_dirpath = os.path.join(grapher.local_dirpath, "k_communities", str(K_COMMUNITIES)) # dir should be already made by cluster maker
    local_csv_filepath = os.path.join(local_dirpath, "retweets.csv")
    print(os.path.abspath(local_csv_filepath))
    if not os.path.exists(local_dirpath):
        os.makedirs(local_dirpath)

    #
    # LOAD DATA
    #

    if os.path.isfile(local_csv_filepath):
        print("LOADING BOT COMMUNITY RETWEETS...")
        df = read_csv(local_csv_filepath)
    else:
        print("DOWNLOADING BOT COMMUNITY RETWEETS...")
        sql = f"""
            SELECT
                bc.community_id

                ,ud.user_id
                ,ud.screen_name_count as user_screen_name_count
                ,ARRAY_TO_STRING(ud.screen_names, ' | ')  as user_screen_names
                ,rt.user_created_at

                ,rt.retweeted_user_id
                ,rt.retweeted_user_screen_name

                ,rt.status_id
                ,rt.status_text
                ,rt.created_at as status_created_at

            FROM `{grapher.bq_service.dataset_address}.{K_COMMUNITIES}_bot_communities` bc -- 681
            JOIN `{grapher.bq_service.dataset_address}.user_details_v2` ud on CAST(ud.user_id  as int64) = bc.user_id
            JOIN `{grapher.bq_service.dataset_address}.retweets_v2` rt on rt.user_id = bc.user_id
            -- ORDER BY 1,2
        """
        counter = 0
        records = []
        for row in grapher.bq_service.execute_query_in_batches(sql):
            records.append({
                "community_id": row.community_id,
                "user_id": row.user_id,
                "user_screen_name_count": row.user_screen_name_count,
                "user_screen_names": row.user_screen_names,
                "user_created_at": dt_to_s(row.user_created_at),

                "retweeted_user_id": row.retweeted_user_id,
                "retweeted_user_screen_name": row.retweeted_user_screen_name,

                "status_id": row.status_id,
                "status_text": row.status_text,
                "status_created_at": dt_to_s(row.status_created_at)
            })
            counter+=1
            if counter % BATCH_SIZE == 0:
                print(logstamp(), fmt_n(counter))

        df = DataFrame(records)
        print(df.head())
        print("WRITING TO FILE...")
        df.to_csv(local_csv_filepath)

    seek_confirmation()

    #
    # ANALYZE DATA
    #

    community_ids = list(df["community_id"].unique())

    for community_id in community_ids:

        community_df = df[df["community_id"] == community_id]

        # USERS MOST RETWEETED

        most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
        most_retweeted_df.columns = list(map(" ".join, most_retweeted_df.columns.values))
        most_retweeted_df = most_retweeted_df.reset_index()
        most_retweeted_df.rename(columns={"status_id nunique": "Retweet Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
        most_retweeted_df.sort_values("Retweet Count", ascending=False, inplace=True)
        most_retweeted_df = most_retweeted_df[:10]
        print(most_retweeted_df)

        most_retweeted_df.sort_values("Retweet Count", ascending=True, inplace=True)
        fig = px.bar(most_retweeted_df,
            x="Retweet Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users Most Retweeted by Bot Community {community_id} (K Communities: {K_COMMUNITIES})"
        )
        if APP_ENV == "development": fig.show()
        local_img_filepath = os.path.join(local_dirpath, f"community-{community_id}-most-retweeted.png")
        fig.write_image(local_img_filepath)

        # USERS WITH MOST RETWEETERS

        most_retweeters_df = community_df.groupby("retweeted_user_screen_name").agg({"user_id": ["nunique"]})
        most_retweeters_df.columns = list(map(" ".join, most_retweeters_df.columns.values))
        most_retweeters_df = most_retweeters_df.reset_index()
        most_retweeters_df.rename(columns={"user_id nunique": "Retweeter Count", "retweeted_user_screen_name": "Retweeted User"}, inplace=True)
        most_retweeters_df.sort_values("Retweeter Count", ascending=False, inplace=True)
        most_retweeters_df = most_retweeters_df[:10]
        print(most_retweeters_df)

        most_retweeters_df.sort_values("Retweeter Count", ascending=True, inplace=True)
        fig_retweeters = px.bar(most_retweeters_df,
            x="Retweeter Count",
            y="Retweeted User",
            orientation="h",
            title=f"Users with Most Retweeters by Bot Community {community_id} (K Communities: {K_COMMUNITIES})"
        )
        if APP_ENV == "development": fig_retweeters.show()
        local_img_filepath = os.path.join(local_dirpath, f"community-{community_id}-most-retweeters.png")
        fig_retweeters.write_image(local_img_filepath)

        # CREATION DATES

        #creation_dates_df = community_df.groupby("user_id").agg({"user_created_at": ["min"]})
        #creation_dates_df["user_created_at"]["min"] = creation_dates_df["user_created_at"]["min"].apply(date_string_conversion)
        #print(creation_dates_df.head())
