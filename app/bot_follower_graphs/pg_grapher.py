from memory_profiler import profile

from networkx import DiGraph

from app import seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.job import Job

BOT_MIN = 0.8
BATCH_SIZE = 100


class BotFollowerGrapher(GraphStorage, Job):
    def __init__(self, pg_service=None, bot_min=BOT_MIN, batch_size=BATCH_SIZE, storage_dirpath=None):
        self.pg_service = pg_service or PgService()
        self.bot_min = bot_min
        self.batch_size = batch_size

        Job.__init__(self)

        storage_dirpath = storage_dirpath or f"bot_follower_graphs/bot_min/{self.bot_min}"
        GraphStorage.__init__(self, dirpath=storage_dirpath)

        print("-------------------------")
        print("BOT FOLLOWER GRAPHER...")
        print("  BOT MIN:", self.bot_min)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"bot_min": self.bot_min, "batch_size": self.batch_size}}

    @profile
    def perform(self):
        self.graph = DiGraph()

        print("FETCHING BOT FOLLOWERS...")
        self.pg_service.fetch_bots_with_followers(bot_min=self.bot_min)
        while True:
            batch = self.pg_service.cursor.fetchmany(size=self.batch_size) # auto-pagination FTW
            if not batch: break # stop the loop when there's nothing left

            for row in batch:
                bot_id = row["bot_id"]
                self.graph.add_edges_from([(follower_id, bot_id) for follower_id in row["follower_ids"]])

            self.counter += len(batch)
            print("  ", logstamp(), "| BOTS:", fmt_n(self.counter))

        self.pg_service.close()
        print("COMPLETE!")


if __name__ == "__main__":

    grapher = BotFollowerGrapher()

    grapher.save_metadata()

    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()

    grapher.write_graph_to_file()
