
#import os
#from dotenv import load_dotenv
from itertools import combinations
from pprint import pprint

from pandas import read_csv

from app.workers.bq_ks2_test_retweeters_two_topics import Analyzer

#load_dotenv()

class Manager:
    """
    For each combination of two topics in a given list of topics,
    performs two-sample KS test on independent populations of users talking about each topic.
    """

    def __init__(self, topics):
        self.topics = topics
        assert len(topics) >= 3

    def supervise(self):
        pass

if __name__ == "__main__":

    # todo: allow customization of topics list via CSV file
    topics = [

        # TAGS
        # "#IGHearing", -- very small sample size
        #"#ImpeachAndConvict",
        #"#TrumpImpeachment",
        #"#IGReport",
        #"#SenateHearing",
        #"#FactsMatter",
        #"#ImpeachmentRally",
        #"#ImpeachmentEve",
        #"#ImpeachAndRemove",
        #"#trumpletter",
        #"#NotAboveTheLaw",
        #"#25thAmendmentNow",
        #"#ShamTrial",
        #"#GOPCoverup",
        #"#MitchMcCoverup",
        #"#AquittedForever",
        #"#CoverUpGOP",
        #"#MoscowMitch",
        #"#CountryOverParty,

        # TERMS
        # 'sham',
        # 'hoax',
        # 'witch',
        # 'Trump',
        # 'Pelosi',
        # 'Schumer',
        # 'Schiff',
        # 'Nadler',
        # 'Yovanovitch',
        # 'Vindman',
        # 'Volker',
        # 'Sondland',
        # 'amigos',
        # 'Fiona Hill',
        # 'George Kent',
        # 'William Taylor',
        # 'Bolton',
        # 'Zelensk',

        # MENTIONS
        '@realDonaldTrump',
        '@senatemajldr',
        '@SpeakerPelosi',
        '@SenSchumer',
        '@JoeBiden',
        '@GOP',
        '@TheDemocrats',
        '@nytimes',
        '@WSJ',
        '@CNN',
        '@MSNBC',
        '@NBCNews',
        '@abcnews',
        '@thehill',
        '@politico',

    ]
    print(f"DETECTED {len(topics)} TOPICS...")

    pairs = list(combinations(topics, 2))
    print(f"ASSEMBLED {len(pairs)} TOPIC PAIRS...")

    for x_topic, y_topic in pairs:
        #print(x_topic, y_topic)

        analyzer = Analyzer(x_topic=x_topic, y_topic=y_topic)

        # todo: only analyze if the topic pair is not already in the csv file! (IDEMPOTENCE CHECK)
        if True:
            pprint(analyzer.report)
            analyzer.append_results_to_csv()
            print("\n\n\n-------------\n\n\n")
