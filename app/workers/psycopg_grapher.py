
from networkx import DiGraph
from memory_profiler import profile

from app.workers.psycopg_base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    @profile
    def perform(self):
        self.nodes = set() # prevents duplicates
        self.edges = set() # prevents duplicates
        self.cursor.execute(self.sql)
        while True:
            results = self.cursor.fetchmany(size=self.batch_size)
            if not results: break
            if not self.dry_run:
                for row in results:
                    user = row["screen_name"]
                    self.nodes.add(user)
                    friends = row["friend_names"]
                    self.nodes.update(friends)
                    #self.edges.update([(user, friend) for friend in friends])
                    for friend in friends:
                        self.edges.add((user, friend))

            self.counter += len(results)
            print(self.generate_timestamp(), "|", self.fmt(self.counter), "|", self.fmt(len(self.nodes)), "|", self.fmt(len(self.edges)))

        #self.nodes = sorted(self.nodes) # takes a long time!
        #self.graph = DiGraph() # todo: construct from self.nodes

if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    #grapher.report()
    #grapher.write_to_file()
