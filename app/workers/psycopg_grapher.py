
from networkx import DiGraph
from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    @profile
    def perform(self):
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

            rr = {"ts": self.generate_timestamp(), "counter": self.counter, "nodes": len(self.graph.nodes), "edges": len(self.graph.edges)}
            print(rr["ts"], "|", self.fmt(rr["counter"]), "|", self.fmt(rr["nodes"]), "|", self.fmt(rr["edges"]))
            self.running_results.append(rr)


if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.write_results_to_file()
    grapher.report()
    #grapher.write_graph_to_file()
