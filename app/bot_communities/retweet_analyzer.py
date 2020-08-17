
import os

from pandas import DataFrame, read_csv
import matplotlib as plt
import plotly.express as px

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

        df = DataFrame(records)
        print(df.head())
        print("WRITING TO FILE...")
        df.to_csv(local_csv_filepath)


    community_ids = list(df["community_id"].unique())

    for community_id in community_ids:

        community_df = df[df["community_id"] == community_id]

        # USERS MOST RETWEETED

        #most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
        ##print(most_retweeted_df.columns.tolist()) #> [('user_id', 'nunique')]
        #most_retweeted_df = most_retweeted_df.reset_index()
        ##print(most_retweeted_df.columns.tolist()) #> [('retweeted_user_screen_name', ''), ('user_id', 'nunique')]
#
        #most_retweeted_df["retweeted_user_screen_name"] = most_retweeted_df[('retweeted_user_screen_name', '')]
        #most_retweeted_df["retweeter_count"] = most_retweeted_df[('user_id', 'nunique')]
        #most_retweeted_df.drop("user_id", axis="columns")
        #most_retweeted_df = most_retweeted_df.sort_values(("user_id", "nunique"), ascending=False)
        #most_retweeted_df = most_retweeted_df[:25]

        #most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})
        #new_df = most_retweeted_df.copy()
        #breakpoint()

        # clean up /reset weird multi-index columns. pandas you're killing me
        #most_retweeted_df = most_retweeted_df.reset_index()
        #most_retweeted_df["retweet_count"] = most_retweeted_df[("status_id", "nunique")]
        #most_retweeted_df.drop("status_id", axis="columns")
        #most_retweeted_df["retweeted_user_screen_name"] = most_retweeted_df[("retweeted_user_screen_name", "")]
        #most_retweeted_df.drop("retweeted_user_screen_name", axis="columns")
        #print(most_retweeted_df.head())
        #breakpoint()
        #most_retweeted_df["retweet_count"] = most_retweeted_df["status_id nunique"]
        #most_retweeted_df = most_retweeted_df.drop("status_id nunique", axis="columns")

        most_retweeted_df = community_df.groupby("retweeted_user_screen_name").agg({"status_id": ["nunique"]})

        most_retweeted_df.columns = list(map(" ".join, most_retweeted_df.columns.values))
        most_retweeted_df = most_retweeted_df.reset_index()
        most_retweeted_df.rename(columns={"status_id nunique": "retweet_count"}, inplace=True)

        most_retweeted_df.sort_values("retweet_count", ascending=False, inplace=True)
        most_retweeted_df = most_retweeted_df[:25]
        print(most_retweeted_df)





        #most_retweeted = most_retweeted_df.to_dict("records")




        # CREATION DATES

        #creation_dates_df = community_df.groupby("user_id").agg({"user_created_at": ["min"]})
        #creation_dates_df["user_created_at"]["min"] = creation_dates_df["user_created_at"]["min"].apply(date_string_conversion)
        #print(creation_dates_df.head())











        #top_sellers = []
        #rank = 1
        #for i, row in product_totals.iterrows():
        #    d = {"rank": rank, "name": row.name, "monthly_sales": row["sales price"]}
        #    top_sellers.append(d)
        #    rank = rank + 1

        #fig = px.bar(df, x="total_bill", y="day", orientation='h')
        #fig.show()
