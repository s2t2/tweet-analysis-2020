
#import os
#from dotenv import load_dotenv
from itertools import combinations
from pprint import pprint

from pandas import read_csv

from app.ks_test.topic_pair_analyzer import Analyzer, RESULTS_CSV_FILEPATH
from app.ks_test.impeachment_topics import IMPEACHMENT_TOPICS
if __name__ == "__main__":

    df = read_csv(RESULTS_CSV_FILEPATH)
    existing_ids = df["topics_id"].tolist()

    topics = IMPEACHMENT_TOPICS
    print(f"DETECTED {len(topics)} TOPICS...")

    pairs = list(combinations(topics, 2))
    print(f"ASSEMBLED {len(pairs)} TOPIC PAIRS...")

    analyzers = [Analyzer(x_topic=xt, y_topic=yt) for xt, yt in pairs]
    analyzers = [analyzer for analyzer in analyzers if analyzer.topics_id not in existing_ids]

    print(f"{len(analyzers)} TOPIC PAIRS NEED TESTING..." )
    for i, analyzer in enumerate(analyzers):
        print("-----------------------------")
        print(f"TESTING TOPIC PAIR {i+1} OF {len(analyzers)} - {analyzer.topics_id.upper()}")
        pprint(analyzer.report)
        analyzer.append_results_to_csv()
