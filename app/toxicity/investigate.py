
from pprint import pprint

from detoxify import Detoxify


if __name__ == '__main__':

    texts = [
        "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…",
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
        "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"
    ]

    # original: bert-base-uncased / Toxic Comment Classification Challenge
    # unbiased: roberta-base / Unintended Bias in Toxicity Classification
    for model_name in ["original", "unbiased"]:

        print("----------------")
        print(model_name.upper())

        model = Detoxify(model_name)

        results = model.predict(texts)
        pprint(results)

        #results_df = DataFrame(results, index=input_text).round(5))
