
import os

from networkx import DiGraph

from app.retweet_graphs_v2.retweet_grapher import RetweetGrapher

BOT_MIN = float(os.getenv("BOT_MIN", default="0.8"))

class BotRetweetGrapher(RetweetGrapher):
    def __init__(self, bot_min=BOT_MIN):
        self.bot_min = float(bot_min)
        super().__init__(storage_dirpath=f"bot_retweet_graphs/bot_min/{self.bot_min}")

    @property
    def metadata(self):
        return {**super().metadata, **{"bot_min": self.bot_min}}

    def perform(self):
        self.results = []
        self.graph = DiGraph()

        for row in self.bq_service.fetch_bot_retweet_edges_in_batches(bot_min=self.bot_min):

            self.graph.add_edge(row["user_id"], row["retweeted_user_id"], weight=row["retweet_count"])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.results.append(self.running_results)
                if self.users_limit and self.counter >= self.users_limit:
                    break


if __name__ == "__main__":

    grapher = BotRetweetGrapher()
    grapher.save_metadata()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
    grapher.save_results()
    grapher.save_graph()
