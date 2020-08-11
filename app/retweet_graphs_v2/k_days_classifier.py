
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days_grapher import get_date_ranges, START_DATE, K_DAYS, N_PERIODS


if __name__ == "__main__":
    print("-------------------------")
    print("K-DAYS GRAPHER...")
    print("  START DATE:", START_DATE)
    print("  K DAYS:", K_DAYS)
    print("  N PERIODS:", N_PERIODS)

    print("-------------------------")
    print("DATE RANGES...")
    date_ranges = get_date_ranges(start_date=START_DATE, k_days=K_DAYS, n_periods=N_PERIODS)
    pprint(date_ranges)
    seek_confirmation()

    for date_range in date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{K_DAYS}/{date_range.start_date}"

        storage = GraphStorage(dirpath=storage_dirpath)
        storage.load_graph()
        storage.report()
