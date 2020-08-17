
import os

from pandas import DataFrame, read_csv

from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.clustering import K_COMMUNITIES
from app.decorators.datetime_decorators import dt_to_s, logstamp
from app.decorators.number_decorators import fmt_n

#from matplotlib import plt
import plotly.express as px
df = px.data.tips()

BATCH_SIZE = 50_000 # we are talking about downloading 1-2M tweets

if __name__ == "__main__":

    print("----------------")
    print("K COMMUNITIES:", K_COMMUNITIES)

    grapher = BotRetweetGrapher()
    local_csv_filepath = os.path.join(grapher.local_dirpath, "k_communities", str(K_COMMUNITIES), "retweets.csv") # dir should be already made by cluster maker
    print(os.path.abspath(local_csv_filepath))

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

        print("WRITING TO FILE...")
        df = DataFrame(records)
        print(df.head())
        df.to_csv(local_csv_filepath)


    breakpoint()

    # todo: dataviz of top retweeted users


    retweeted_users = []

    fig = px.bar(df, x="total_bill", y="day", orientation='h')
    fig.show()





    # todo: dataviz of user creation dates for each community
