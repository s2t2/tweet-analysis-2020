
import psycopg2
from networkx import DiGraph
from memory_profiler import profile

from app import APP_ENV
from app.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
from app.workers import DRY_RUN, BATCH_SIZE, USERS_LIMIT, fmt_ts, fmt_n
from app.friend_graphs.base_grapher import BaseGrapher

class PsycopgGrapher(BaseGrapher):
    def __init__(self, dry_run=DRY_RUN, batch_size=BATCH_SIZE, users_limit=USERS_LIMIT,
                        database_url=DATABASE_URL, table_name=USER_FRIENDS_TABLE_NAME):
        super().__init__(dry_run=dry_run, batch_size=batch_size, users_limit=users_limit)
        self.database_url = database_url
        self.table_name = table_name
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor(name="network_grapher", cursor_factory=psycopg2.extras.DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!

    @property
    def metadata(self):
        return {**super().metadata, **{"database_url": self.database_url, "table_name": self.table_name}} # merges dicts

    @property
    def sql(self):
        query = f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {self.table_name} "
        if self.users_limit:
            query += f"LIMIT {self.users_limit};"
        return query

    @profile
    def perform(self):
        self.start()
        self.write_metadata_to_file()
        self.upload_metadata()

        print(fmt_ts(), "CONSTRUCTING GRAPH OBJECT...")
        self.graph = DiGraph()
        self.running_results = []
        self.cursor.execute(self.sql)
        while True:
            batch = self.cursor.fetchmany(size=self.batch_size)
            if not batch: break
            self.counter += len(batch)

            if not self.dry_run:
                for row in batch:
                    self.graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])

            rr = {"ts": fmt_ts(), "counter": self.counter, "nodes": len(self.graph.nodes), "edges": len(self.graph.edges)}
            print(rr["ts"], "|", fmt_n(rr["counter"]), "|", fmt_n(rr["nodes"]), "|", fmt_n(rr["edges"]))
            self.running_results.append(rr)

        self.cursor.close()
        self.connection.close()
        print(fmt_ts(), "GRAPH CONSTRUCTED!")
        self.report()

        self.write_results_to_file()
        self.upload_results()

        self.write_graph_to_file()
        self.upload_graph()

        self.end()


if __name__ == "__main__":

    grapher = PsycopgGrapher.cautiously_initialized()

    grapher.perform()
