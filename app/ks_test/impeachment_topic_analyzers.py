
from pprint import pprint

from pandas import read_csv

from app.ks_test.topic_analyzer import Analyzer, RESULTS_CSV_FILEPATH
from app.ks_test.impeachment_topics import IMPEACHMENT_TOPICS

if __name__ == "__main__":

    df = read_csv(RESULTS_CSV_FILEPATH)
    existing_ids = df["row_id"].tolist()

    topics = IMPEACHMENT_TOPICS # todo: topic customization
    print(f"DETECTED {len(topics)} TOPICS...")

    analyzers = [Analyzer(topic=topic) for topic in topics]
    analyzers = [analyzer for analyzer in analyzers if analyzer.row_id not in existing_ids]

    print(f"{len(analyzers)} TOPICS NEED TESTING..." )
    for i, analyzer in enumerate(analyzers):
        print("-----------------------------")
        print(f"TESTING TOPIC {i+1} OF {len(analyzers)}: '{analyzer.row_id.upper()}'")
        pprint(analyzer.report)
        analyzer.append_results_to_csv(RESULTS_CSV_FILEPATH)
