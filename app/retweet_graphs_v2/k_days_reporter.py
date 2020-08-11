
import os
from pandas import DataFrame

from app import DATA_DIR
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator


if __name__ == "__main__":

    gen = DateRangeGenerator()

    reports = []
    for date_range in gen.date_ranges:
        storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}")
        report = {**storage.memory_report, **{"k_days": gen.k_days, "start_date": date_range.start_date}}
        reports.append(report)

    df = DataFrame(reports)
    print(df.head())
    df.to_csv(os.path.join(DATA_DIR, "retweet_graphs_v2", "k_days", "graph_reports.csv"))
