
import os
from pprint import pprint

from pandas import read_csv

from app.ks_test.topic_analyzer import TopicAnalyzer, RESULTS_CSV_FILEPATH
from app.ks_test.impeachment_topics import IMPEACHMENT_TOPICS # todo: allow customization of topics list via CSV file

if __name__ == "__main__":

    if os.path.isfile(RESULTS_CSV_FILEPATH):
        df = read_csv(RESULTS_CSV_FILEPATH)
        existing_ids = df["row_id"].tolist()
    else:
        existing_ids = []

    topics = IMPEACHMENT_TOPICS # todo: topic customization
    print(f"DETECTED {len(topics)} TOPICS...")

    analyzers = [TopicAnalyzer(topic=topic) for topic in topics]
    analyzers = [analyzer for analyzer in analyzers if analyzer.row_id not in existing_ids]

    print(f"OF WHICH {len(analyzers)} NEED TESTING..." )
    for i, analyzer in enumerate(analyzers):
        print("-----------------------------")
        print(f"TESTING TOPIC {i+1} OF {len(analyzers)}: '{analyzer.row_id.upper()}'")
        pprint(analyzer.report)
        analyzer.append_results_to_csv(RESULTS_CSV_FILEPATH)
