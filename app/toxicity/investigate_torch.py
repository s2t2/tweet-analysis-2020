
from pprint import pprint

from detoxify import Detoxify
#import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pandas import DataFrame

if __name__ == '__main__':

    # https://huggingface.co/unitary/toxic-bert?text=I+like+you.+I+love+you
    # https://huggingface.co/transformers/usage.html
    # https://huggingface.co/transformers/model_doc/bert.html#bertforsequenceclassification
    model_name = "unitary/toxic-bert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print("MODEL:", model_name, type(model))

    texts = [
        "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…",
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
        "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"
    ]

    # https://huggingface.co/models?search=tox
    #torch_models = [
    #    #"toxic_bert", #> ImportError: cannot import name 'toxic_albert' from 'detoxify' (/opt/anaconda3/envs/tweet-analyzer-env-38/lib/python3.8/site-packages/detoxify/__init__.py)
    #    #"unbiased_toxic_roberta" #> ImportError: cannot import name 'toxic_albert' from 'detoxify' (/opt/anaconda3/envs/tweet-analyzer-env-38/lib/python3.8/site-packages/detoxify/__init__.py)
    #    "toxic-bert",
    #    "unbiased-toxic-roberta"
    #]

    for text in texts:
        print("----------------")
        print(f"TEXT:")
        print(text)

        records = []
        #for repo_owner, repo_name in torch_models:
        #    #model = torch.hub.load("unitaryai/detoxify")
        #    model = torch.hub.load(repo_owner, repo_name)
        #    record = model.predict(text)
        #    record["model_name"] = repo_name
        #    records.append(record)

        # https://pytorch.org/docs/stable/hub.html
        #model_name = "unitary/toxic-bert"
        #model = torch.hub.load(model_name)
        #scores = model.predict(text)





        breakpoint()
        scores = model(text)

        record = scores
        record["model_name"] = model_name
        records.append(record)

        df = DataFrame(records)
        print(df.round(8).head())
