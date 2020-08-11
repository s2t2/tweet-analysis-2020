
from app import server_sleep
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator
from app.retweet_graphs_v2.retweet_grapher import RetweetGrapher


if __name__ == "__main__":

    gen = DateRangeGenerator()

    bq_service = BigQueryService()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"

        grapher = RetweetGrapher(storage_dirpath=storage_dirpath, bq_service=bq_service,
            tweets_start_at=date_range.start_at, tweets_end_at=date_range.end_at
        )
        grapher.save_metadata()
        grapher.start()
        grapher.perform()
        grapher.end()
        grapher.report()
        grapher.save_results()
        grapher.save_graph()

        del grapher # clearing graph from memory
        print("\n\n\n\n")

    print("JOB COMPLETE!")

    server_sleep()
