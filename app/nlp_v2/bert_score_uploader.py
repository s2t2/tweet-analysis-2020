
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator

if __name__ == "__main__":
    bq_service = BigQueryService()

    for dr in DateRangeGenerator(start_date="2020-12-20", k_days=1, n_periods=58).date_ranges:
        print(dr.start_date)
