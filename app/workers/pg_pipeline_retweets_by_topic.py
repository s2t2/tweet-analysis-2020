

from app.pg_pipeline import Pipeline

DEFAULT_TOPICS = ["#MAGA", "#MoscowMitch", "#FactsMatter", "#GOPCoverup",
    "#ImpeachAndRemove", "#ImpeachAndConvict", "#25thAmendmentNow", "#CountryOverParty"
    "#TrumpImpeachment", "#ImpeachmentEve",
    "#IGReport", "#CountryOverParty",
    "#ShamTrial", "#AquittedForever", "#NotAboveTheLaw"
    "#Hoax"
]



if __name__ == "__main__":

    pipeline = Pipeline()
    pipeline.migrate_populate_retweets_by_topic(DEFAULT_TOPICS)
    pipeline.report()
    pipeline.sleep()
