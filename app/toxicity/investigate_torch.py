
from pprint import pprint

from detoxify import Detoxify
import torch
from pandas import DataFrame

if __name__ == '__main__':

    texts = [
        "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…",
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
        "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"
    ]

    model_names = [
        "toxic_bert", #> ImportError: cannot import name 'toxic_albert' from 'detoxify' (/opt/anaconda3/envs/tweet-analyzer-env-38/lib/python3.8/site-packages/detoxify/__init__.py)
        "unbiased_toxic_roberta" #> ImportError: cannot import name 'toxic_albert' from 'detoxify' (/opt/anaconda3/envs/tweet-analyzer-env-38/lib/python3.8/site-packages/detoxify/__init__.py)
    ]

    for text in texts:

        print("----------------")
        print(f"TEXT: '{text}'")

        records = []
        for model_name in model_names:
            model = torch.hub.load("unitaryai/detoxify", model_name)
            record = model.predict(text)
            record["model_name"] = model_name
            records.append(record)

        print(f"SCORES:")

        #df = DataFrame(records, columns=["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_hate", "model"])
        df = DataFrame(records)
        print(df.round(8).head())
