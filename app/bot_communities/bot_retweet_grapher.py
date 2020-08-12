
import os
#from pandas import read_csv

#from app.bq_service import BigQueryService
from retweet_graphs_v2.retweet_grapher import RetweetGrapher

BOT_MIN = int(os.getenv("BOT_MIN", default="0.8"))

class BotRetweetGrapher(RetweetGrapher):
    def __init__(self, bot_min=BOT_MIN):
        self.bot_min = float(bot_min)
        super().__init__(storage_dirpath="bot_retweet_graphs/bot_min/{self.bot_min}")

    def perform(self):
        for row in self.bq_service.fetch_bot_retweet_edges_in_batches(bot_min=self.bot_min):
            print(row.user_id)

if __name__ == "__main__":

    storage_dirpath = f

    grapher = BotRetweetGrapher(storage_dirpath=storage_dirpath)

    breakpoint()

    grapher.save_metadata()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
    grapher.save_results()
    grapher.save_graph()
