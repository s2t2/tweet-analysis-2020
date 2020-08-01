
from networkx import DiGraph
from memory_profiler import profile

from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n

from app.friend_graphs.psycopg_grapher import PsycopgGrapher

class Grapher(PsycopgGrapher):

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
                    self.edges += [(row["screen_name"], friend) for friend in row["friend_names"]]

            rr = {"ts": logstamp(), "counter": self.counter, "edges": len(self.edges)}
            print(rr["ts"], "|", fmt_n(rr["counter"]), "|", fmt_n(rr["edges"]))
            self.running_results.append(rr)

        self.write_results_to_file()
        self.upload_results()

        self.write_edges_to_file()
        self.upload_edges()

        print(logstamp(), "CONSTRUCTING GRAPH OBJECT...")
        self.graph = DiGraph(self.edges)
        print(logstamp(), "GRAPH CONSTRUCTED!")
        del self.edges # try to free up some memory maybe, before writing to file
        self.report()

        self.write_graph_to_file()
        self.upload_graph()

        self.end()

if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()

    grapher.perform()

    grapher.sleep()
