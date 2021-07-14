
from pprint import pprint

from detoxify import Detoxify
from pandas import DataFrame

if __name__ == '__main__':

    texts = [
        "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…",
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
        "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"
    ]

    # original: bert-base-uncased / Toxic Comment Classification Challenge
    original = Detoxify("original")

    # unbiased: roberta-base / Unintended Bias in Toxicity Classification
    unbiased = Detoxify("unbiased")

    for text in texts:

        print("----------------")
        print(f"TEXT: '{text}'")

        original_results = original.predict(text)
        #original_results["text"] = text
        original_results["model"] = "original"

        unbiased_results = unbiased.predict(text)
        #unbiased_results["text"] = text
        unbiased_results["model"] = "unbiased"

        print(f"SCORES:")

        records = [original_results, unbiased_results]
        df = DataFrame(records, columns=["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_hate", "model"])
        print(df.round(8).head())
