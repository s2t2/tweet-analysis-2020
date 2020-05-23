
from networkx import DiGraph
#from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    #@profile
    def perform(self):
        self.start()
        self.graph = DiGraph()
        self.cursor.execute(self.sql)
        while True:
            results = self.cursor.fetchmany(size=self.batch_size)
            if not results: break
            self.counter += len(results)
            print(self.generate_timestamp(), self.counter)
            if not self.dry_run:
                for row in results:
                    user = row["screen_name"]
                    friends = row["friend_names"]
                    self.graph.add_node(user)
                    self.graph.add_nodes_from(friends)
                    self.graph.add_edges_from([(user, friend) for friend in friends])
        self.end()


if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.perform()
    grapher.write_graph_to_file()
