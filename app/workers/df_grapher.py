
#from app.workers.network_grapher import NetworkGrapher
#
#class DataFrameGrapher(NetworkGrapher):
#    def perform(self):
#        self.counter = 1
#        self.batch = []
#        self.start_at = time.perf_counter()
#        for row in self.bq.fetch_user_friends_in_batches():
#            self.batch.append(row)
#            self.counter+=1
#            if self.counter % 1000 == 0:
#                print(generate_timestamp(), self.counter)
#
#                self.batch = []
#        self.end_at = time.perf_counter()
#
#if __name__ == "__main__":
