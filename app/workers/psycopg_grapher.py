import os

from networkx import DiGraph
from pandas import DataFrame
from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    @profile
    def perform(self):
        #self.nodes = set() # prevents duplicates
        #self.edges = set() # prevents duplicates
        self.graph = DiGraph()

        self.running_results = []
        self.cursor.execute(self.sql)
        while True:
            batch = self.cursor.fetchmany(size=self.batch_size)
            if not batch: break
            if not self.dry_run:
                for row in batch:
                    self.graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])
            self.counter += len(batch)

            batch_stamp = self.generate_timestamp()
            rr = {"ts": batch_stamp, "counter": self.counter, "nodes": len(self.graph.nodes), "edges": len(self.graph.edges)}
            self.running_results.append(rr)
            print(batch_stamp, "|", self.fmt(rr["counter"]), "|", self.fmt(rr["nodes"]), "|", self.fmt(rr["edges"]))

    def write_results_csv(self, csv_filepath=None):
        csv_filepath = csv_filepath or os.path.join(self.data_dir, f"results_{self.ts_id}.csv")
        print("WRITING RUNNING RESULTS TO:", os.path.abspath(csv_filepath))
        df = DataFrame(self.running_results)
        df.to_csv(csv_filepath)


if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.write_results_csv()
    grapher.report()
    #grapher.write_graph_to_file()
