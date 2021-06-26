
import os
from pprint import pprint

from dotenv import load_dotenv
from detoxify import Detoxify
from pandas import DataFrame

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", default="original")

def rounded_score(score):
    return round(score, 8)

if __name__ == '__main__':

    print("----------------")
    print("MODEL:", MODEL_NAME.upper())

    model = Detoxify(MODEL_NAME)
    print(model)

    print("----------------")
    print("TEXTS...")

    rows = [
        {"status_ids": [1,2,3,4],   "status_text": "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…"},
        {"status_ids": [5,6,7],     "status_text": "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…"},
        {"status_ids": [8,9,10,11], "status_text": "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…"},
        {"status_ids": [12,13,14],  "status_text": "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"}
    ]

    print("----------------")
    print("SCORING...")

    records = []
    for row in rows:
        status_ids = row["status_ids"]
        status_text = row["status_text"]

        scores = model.predict(status_text)

        record = {
            "status_text": status_text,
            "status_ids": status_ids,

            "identity_hate": rounded_score(scores["identity_hate"]),
            "insult": rounded_score(scores["insult"]),
            "obscene": rounded_score(scores["obscene"]),
            "severe_toxicity": rounded_score(scores["severe_toxicity"]),
            "threat": rounded_score(scores["threat"]),
            "toxicity": rounded_score(scores["toxicity"]),
        }
        pprint(record)

        records.append(record)

    #df = DataFrame(records)
    #print(df.head())
