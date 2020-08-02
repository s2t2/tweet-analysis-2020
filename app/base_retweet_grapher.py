



class BaseRetweetGrapher(GraphStorage):

    def __init__(self, job_id=None):
        """
        Parent class with helper methods for assembling the retweet graph object.

        Is able to write graph objects to file and upload them to Google Cloud Storage.

        Graph construction should be done in child class' perform() method.

        Example:
            grapher = BaseGrapher.cautiously_initialized()
            grapher.start()
            grapher.perform()
            grapher.end()
            grapher.report()

        Params:
            job_id (str / None)
                A unique identifer to associate a given job's results files.
                Is used as part of local filepaths and remote bucket paths, so should avoid including spaces or special characters.
                Assigns a timestamp-based unique identifier by default.
        """
        self.job_id = (job_id or dt.now().strftime("%Y-%m-%d-%H%M"))
        self.dry_run = (dry_run == True)



        self.gcs_dirpath = os.path.join("storage", "data", "retweet_graphs", self.job_id)

        self.local_dirpath = os.path.join(DATA_DIR, "retweet_graphs", self.job_id)

        print("-------------------------")
        print("GRAPHER CONFIG...")
        print("  JOB ID:", self.job_id)
        print("  DRY RUN:", str(self.dry_run).upper())
        print("-------------------------")
        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        service.init_local_dir()












    def init_local_dir(self):
        if not os.path.exists(self.local_dirpath):
            os.mkdir(self.local_dirpath)


    @property
    def metadata(self):
        return {"app_env": APP_ENV, "job_id": self.job_id, "dry_run": self.dry_run}

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.start_at = time.perf_counter()
        self.counter = 0

    def perform(self):
        """To be overridden by child class"""
        self.graph = DiGraph()

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {fmt_n(self.counter)} USERS IN {fmt_n(self.duration_seconds)} SECONDS")

    def report(self):
        print("NODES:", fmt_n(len(self.graph.nodes)))
        print("EDGES:", fmt_n(len(self.graph.edges)))
        print("SIZE:", fmt_n(self.graph.size()))

    def sleep(self):
        if APP_ENV == "production":
            print("SLEEPING...")
            time.sleep(12 * 60 * 60) # twelve hours, more than enough time to stop the server

if __name__ == "__main__":


    #grapher = BaseGrapher(job_id="2020-05-27-1537")
    #grapher.upload_edges()

    grapher = BaseGrapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
