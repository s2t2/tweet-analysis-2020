
import os
from pandas import DataFrame

from app import DATA_DIR
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator


if __name__ == "__main__":

    gen = DateRangeGenerator()

    reports = []
    for date_range in gen.date_ranges:
        storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}")

        try:
            report = {**storage.memory_report, **{"k_days": gen.k_days, "start_date": date_range.start_date}}
            reports.append(report)
        except Exception as err:
            print("OOPS", date_range.start_date, err)

    df = DataFrame(reports)
    print(df.head())
    local_graph_report_filepath = os.path.join(DATA_DIR, "retweet_graphs_v2", "k_days", str(gen.k_days), "graph_reports.csv")
    print("WRITING TO CSV...", os.path.abspath(local_graph_report_filepath))
    df.to_csv(local_graph_report_filepath)
