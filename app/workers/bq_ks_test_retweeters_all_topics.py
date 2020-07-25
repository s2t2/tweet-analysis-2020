
from pprint import pprint

from pandas import read_csv

from app.workers.bq_ks_test_retweeters_by_topic import Analyzer, RESULTS_CSV_FILEPATH

if __name__ == "__main__":

    df = read_csv(RESULTS_CSV_FILEPATH)
    existing_ids = df["row_id"].tolist()

    # todo: allow customization of topics list via CSV file
    topics = [
        # TAGS
        "#MAGA",
        # "#IGHearing", -- very small sample size
        "#ImpeachAndConvict",
        "#TrumpImpeachment",
        "#IGReport",
        "#SenateHearing",
        "#FactsMatter",
        "#ImpeachmentRally",
        "#ImpeachmentEve",
        "#ImpeachAndRemove",
        "#trumpletter",
        "#NotAboveTheLaw",
        "#25thAmendmentNow",
        "#ShamTrial",
        "#GOPCoverup",
        "#MitchMcCoverup",
        "#AquittedForever",
        "#CoverUpGOP",
        "#MoscowMitch",
        "#CountryOverParty",

        # TERMS
        #'sham',
        #'hoax',
        #'witch', -- could be witchhunt or witch-hunt or just witch
        'Trump',
        'Pelosi',
        'Schumer',
        'Schiff',
        'Nadler',
        #'Yovanovitch', # low sample size
        'Vindman',
        #'Volker', # low sample size
        'Sondland',
        # 'amigos', # low sample size
        'Bolton',
        'Zelensk',
        'Fiona', # 'Fiona Hill',
        'Kent', # 'George Kent',
        'Taylor', # 'William Taylor',

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

    analyzers = [Analyzer(topic=topic) for topic in topics]
    analyzers = [analyzer for analyzer in analyzers if analyzer.row_id not in existing_ids]

    print(f"{len(analyzers)} TOPICS NEED TESTING..." )
    for i, analyzer in enumerate(analyzers):
        print("-----------------------------")
        print(f"TESTING TOPIC {i+1} OF {len(analyzers)}: '{analyzer.row_id.upper()}'")
        pprint(analyzer.report)
        analyzer.append_results_to_csv(RESULTS_CSV_FILEPATH)
