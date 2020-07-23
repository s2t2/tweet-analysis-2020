
import os
from pprint import pprint

from dotenv import load_dotenv

from app import DATA_DIR
from app.ks_test_helper import Analyzer

load_dotenv()

RESULTS_CSV_FILEPATH = os.path.join(DATA_DIR, "retweeter_ks_test_results.csv")

if __name__ == "__main__":

    analyzer = Analyzer()
    pprint(analyzer.report)
    analyzer.append_results_to_csv(RESULTS_CSV_FILEPATH)
