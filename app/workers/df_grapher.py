
from app.workers.network_grapher import NetworkGrapher

class DataFrameGrapher(NetworkGrapher):
    def perform(self):
        self.counter = 1
        self.start_at = time.perf_counter()
        #for row in self.bq.fetch_user_friends_in_batches():
        #    user = row["screen_name"]
        #    friends = row["friend_names"]
        #    self.graph.add_node(user)
        #    self.graph.add_nodes_from(friends)
        #    self.graph.add_edges_from([(user, friend) for friend in friends])
        #    self.counter+=1
        #    if self.counter % 1000 == 0: print(generate_timestamp(), self.counter)
        # TODO
        print("NETWORK GRAPH COMPLETE!")
        self.end_at = time.perf_counter()

if __name__ == "__main__":
