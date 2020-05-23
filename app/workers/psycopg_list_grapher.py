
from networkx import DiGraph
from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    @profile
    def perform(self):
        self.edges = []
        self.running_results = []
        self.start()

        self.cursor.execute(self.sql)
        while True:
            batch = self.cursor.fetchmany(size=self.batch_size)
            if not batch: break
            self.counter += len(batch)

            if not self.dry_run:
                for row in batch:
                    user = row["screen_name"]
                    friends = row["friend_names"]
                    self.edges += [(user, friend) for friend in friends]

            rr = {"ts": self.generate_timestamp(), "counter": self.counter, "edges": len(self.edges)}
            print(rr["ts"], "|", self.fmt(rr["counter"]), "|", self.fmt(rr["edges"]))
            self.running_results.append(rr)

        self.write_results_to_file()
        self.write_edges_to_file()

        print(self.generate_timestamp(), "CONSTRUCTING GRAPH OBJECT...")
        self.graph = DiGraph(self.edges)
        print(self.generate_timestamp(), "GRAPH CONSTRUCTED!")
        self.write_graph_to_file()

        self.end()


if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()

    grapher.perform()
    grapher.report()
