
import os
from pprint import pprint
from itertools import combinations

from pandas import read_csv

from app.ks_test.topic_pair_analyzer import TopicPairAnalyzer, RESULTS_CSV_FILEPATH
from app.ks_test.impeachment_topics import IMPEACHMENT_TOPICS # todo: allow customization of topics list via CSV file

if __name__ == "__main__":

    if os.path.isfile(RESULTS_CSV_FILEPATH):
        df = read_csv(RESULTS_CSV_FILEPATH)
        existing_ids = df["row_id"].tolist()
    else:
        existing_ids = []

    topics = IMPEACHMENT_TOPICS
    print(f"DETECTED {len(topics)} TOPICS...")

    topic_pairs = list(combinations(topics, 2))
    print(f"COMBINED INTO {len(topic_pairs)} TOPIC PAIRS...")

    analyzers = [TopicPairAnalyzer(x_topic=xt, y_topic=yt) for xt, yt in topic_pairs]
    analyzers = [analyzer for analyzer in analyzers if analyzer.row_id not in existing_ids]

    print(f"OF WHICH {len(analyzers)} NEED TESTING..." )
    for i, analyzer in enumerate(analyzers):
        print("-----------------------------")
        print(f"TESTING TOPIC PAIR {i+1} OF {len(analyzers)} - {analyzer.row_id.upper()}")
        pprint(analyzer.report)
        analyzer.append_results_to_csv()
