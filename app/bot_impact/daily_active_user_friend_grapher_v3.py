
import os
from memory_profiler import profile
from functools import lru_cache

from pandas import DataFrame, read_csv
from networkx import DiGraph
import matplotlib.pyplot as plt
from numpy import quantile, logical_or

from app import seek_confirmation, APP_ENV
from app.decorators.number_decorators import fmt_n, fmt_pct
from app.job import Job
from app.bq_service import BigQueryService
from app.bot_impact.friend_graph_storage import FriendGraphStorage

DATE = os.getenv("DATE", default="2020-02-05")
TWEET_MIN = int(os.getenv("TWEET_MIN", default="4"))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1000"))
LIMIT = os.getenv("LIMIT") # default none, but maybe use 10000


class DailyFriendGrapher(FriendGraphStorage, Job):
    def __init__(self, bq_service=None, date=DATE, tweet_min=TWEET_MIN, batch_size=BATCH_SIZE, limit=LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.date = date
        self.tweet_min = tweet_min
        self.batch_size = batch_size
        self.limit = limit

        Job.__init__(self)
        FriendGraphStorage.__init__(self, dirpath=f"active_tweeter_friend_graphs_v3/{self.date}/tweet_min/{self.tweet_min}")

        self.nodes = None
        self.graph = None
        self.subgraph = None

        print("-------------------------")
        print("DAILY FRIEND GRAPHER V2...")
        print("  TWEET MIN:", self.tweet_min)
        print("  DATE:", self.date)
        print("  LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"bq_service": self.bq_service.metadata, "tweet_min": self.tweet_min, "date": self.date, "batch_size": self.batch_size,"limit":self.limit}}

    @profile
    def fetch_nodes(self):
        self.start()
        self.nodes = []
        print("FETCHING DAILY ACTIVE TWEETERS AND THEIR FRIENDS...")
        for row in self.bq_service.fetch_daily_active_user_friends_v3(date=self.date, tweet_min=self.tweet_min, limit=self.limit):
            self.nodes.append(dict(row))

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()
        self.end()

    @property
    @lru_cache(maxsize=None)
    def nodes_df(self):
        if os.path.isfile(self.local_nodes_filepath):
            return read_csv(self.local_nodes_filepath)

        if not self.nodes:
            self.fetch_nodes()

        df = DataFrame(self.nodes)
        del self.nodes
        lower_max = quantile(df["mean_opinion"], 0.05) #> ~0
        upper_min = quantile(df["mean_opinion"], 0.95) #> ~1
        print("LOWER:", lower_max, "| UPPER:", upper_min)

        df["stubborn"] = 1 * logical_or(df["mean_opinion"] <= lower_max, df["mean_opinion"] >= upper_min) # 1 if below the low or above the high, else 0
        print("STUBBORN:", fmt_pct(len(df[df["stubborn"] == 1]) / len(df)))
        print(df["stubborn"].value_counts())

        return df

    def generate_mean_opinions_histogram(self):
        plt.hist(self.nodes_df["mean_opinion"])
        plt.grid()
        plt.title(f"Distribution of Mean Opinion Scores for Active Tweeters on {self.date}")
        plt.xlabel("Mean Opinion Score (0:left, 1:right)")
        plt.ylabel(f"User Count (>= {self.tweet_min} Tweets)")
        if APP_ENV == "development":
            plt.show()
        plt.savefig(self.local_histogram_filepath)
        self.upload_file(self.local_histogram_filepath, self.gcs_histogram_filepath)

    @profile
    def compile_graph(self):
        self.start()

        self.graph = DiGraph()
        print("COMPILING FRIEND GRAPH...")
        for i, row in self.nodes_df.iterrows():
            self.graph.add_edges_from([(row["screen_name"], friend_name) for friend_name in row["friend_names"]])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()

        self.end()



if __name__ == "__main__":

    # for all tweets on a given day,
    # ... assemble a friend graph between all ACTIVE tweeters and the people they follow
    # ... with edge format: (follower, following1)
    # ... and save to gpickle and upload to GCS
    # ... also create a subgraph and save to gpickle and upload to GCS:

    grapher = DailyFriendGrapher()
    grapher.save_metadata()

    print(grapher.nodes_df.columns.tolist())
    print(grapher.nodes_df.head())
    #grapher.nodes_df[""].value_counts(normalize=True, bin=)
    #grapher.nodes_df[""].value_counts()

    grapher.save_nodes()
    grapher.generate_mean_opinions_histogram()

    grapher.compile_graph()
    grapher.graph_report()
    grapher.save_graph()

    exit()

    grapher.compile_subgraph()
    grapher.subgraph_report()
    grapher.save_subgraph()
