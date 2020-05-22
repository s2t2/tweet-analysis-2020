
from networkx import DiGraph
from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    @profile
    def perform(self):
        self.nodes = set() # using a set to prevent duplicate values from being added
        self.cursor.execute(self.sql)
        while True:
            results = self.cursor.fetchmany(size=self.batch_size)
            if not results: break
            self.counter += len(results)
            print(self.generate_timestamp(), self.counter, len(self.nodes))

            if not self.dry_run:
                for row in results:
                    self.nodes.add(row["screen_name"])
                    #for friend_name in row["friend_names"]:
                    #    self.nodes.add(friend_name)
                    self.nodes.update(row["friend_names"])

        print("NODES:", len(self.nodes))
        #self.nodes = sorted(self.nodes) # takes a long time!
        self.graph = DiGraph() # todo: construct from self.nodes

if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.write_to_file()
