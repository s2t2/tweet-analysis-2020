
#
# adapted from: https://github.com/unitaryai/detoxify/blob/master/detoxify/detoxify.py
#
# using the pre-trained toxicity models provided via Detoxify checkpoints, but...
# 1) let's try different / lighter torch requirement approaches (to enable installation on heroku) - see requirements.txt file
# 2) let's also try to return the raw scores (to save processing time)
#
# references:
#   https://github.com/unitaryai/detoxify/blob/master/detoxify/detoxify.py
#   https://pytorch.org/docs/stable/hub.html
#   https://pytorch.org/docs/stable/hub.html#torch.hub.load_state_dict_from_url
#   https://pytorch.org/docs/stable/generated/torch.no_grad.html
#

import os
from pprint import pprint
from functools import lru_cache

from dotenv import load_dotenv
import torch
import transformers
from pandas import DataFrame

load_dotenv()

CHECKPOINT_NAME = os.getenv("CHECKPOINT_NAME", default="original") # "original" or "unbiased" (see README)

CHECKPOINT_URLS = {
    "original": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_original-c1212f89.ckpt",
    "unbiased": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_bias-4e693588.ckpt",
    #"multilingual": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_multilingual-bbddc277.ckpt",
    #"original-small": "https://github.com/unitaryai/detoxify/releases/download/v0.1.2/original-albert-0e1d6498.ckpt",
    #"unbiased-small": "https://github.com/unitaryai/detoxify/releases/download/v0.1.2/unbiased-albert-c8519128.ckpt"
}

class ModelManager:
    def __init__(self, checkpoint_name=None):
        self.checkpoint_name = checkpoint_name or CHECKPOINT_NAME
        self.checkpoint_url = CHECKPOINT_URLS[self.checkpoint_name]

        self.model_state = None

        self.state_dict = None
        self.config = None

        self.tokenizer_name = None
        self.model_name = None
        self.model_type = None
        self.num_classes = None
        self.class_names = None



    def load_model_state(self):
        """Loads pre-trained model from saved checkpoint metadata."""
        if not self.model_state:
            print("---------------------------")
            print("LOADING MODEL STATE...")
            # see: https://pytorch.org/docs/stable/hub.html#torch.hub.load_state_dict_from_url
            self.model_state = torch.hub.load_state_dict_from_url(self.checkpoint_url, map_location="cpu")

            self.state_dict = self.model_state["state_dict"]
            self.config = self.model_state["config"]

            self.tokenizer_name = self.config["arch"]["args"]["tokenizer_name"] #> BertTokenizer
            self.model_name = self.config["arch"]["args"]["model_name"] #> BertForSequenceClassification
            self.model_type = self.config["arch"]["args"]["model_type"] #> bert-base-uncased
            self.num_classes = self.config["arch"]["args"]["num_classes"] #> 6
            self.class_names = self.config["dataset"]["args"]["classes"] #> ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']

            print("---------------------------")
            print("MODEL TYPE:", self.model_type)
            print("MODEL NAME:", self.model_name)
            print("TOKENIZER NAME:", self.tokenizer_name)
            print(f"CLASS NAMES ({self.num_classes}):", self.class_names)

    @property
    @lru_cache(maxsize=None)
    def model(self):
        if not self.model_state and self.model_name and self.model_type and self.num_classes and self.state_dict:
            self.load_model_state()

        # see: https://huggingface.co/transformers/main_classes/model.html#transformers.PreTrainedModel.from_pretrained
        return getattr(transformers, self.model_name).from_pretrained(
            pretrained_model_name_or_path=None,
            config=self.model_type,
            num_labels=self.num_classes,
            state_dict=self.state_dict,
            _fast_init=False # provides better results? see: https://github.com/unitaryai/detoxify/pull/20#discussion_r664069305 ... after adding this we're now saving the results to the "_slow" tables
        )

    @property
    @lru_cache(maxsize=None)
    def tokenizer(self):
        if not self.model_state and self.tokenizer_name and self.model_type:
            self.load_model_state()

        return getattr(transformers, self.tokenizer_name).from_pretrained(self.model_type)

    @torch.no_grad()
    def predict_scores(self, texts):
        """Returns the raw scores, without formatting (for those desiring a faster experience)."""
        self.model.eval()
        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True).to(self.model.device)
        out = self.model(**inputs)[0]
        scores = torch.sigmoid(out).cpu().detach().numpy()
        return scores

    def predict_records(self, texts):
        """Optional, if you want the scores returned as a list of dict, with the texts in there as well."""
        records = []
        for i, score_row in enumerate(self.predict_scores(texts)):
            record = {}
            record["text"] = texts[i]
            for class_index, class_name in enumerate(self.class_names):
                record[class_name] = float(score_row[class_index])
            records.append(record)
        return records

    def predict_df(self, texts):
        """Optional, if you want the scores returned as a dataframe."""
        return DataFrame(self.predict_records(texts))


if __name__ == '__main__':

    texts = [
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
    ]

    mgr = ModelManager()

    mgr.load_model_state()

    print("------------")
    print("MODEL:", type(mgr.model))
    print("TOKENIZER:", type(mgr.tokenizer))

    scores = mgr.predict_scores(texts)
    print("------------")
    print("SCORES:", type(scores), scores.shape)
    print(scores[0])

    records = mgr.predict_records(texts)
    print("------------")
    print("RECORDS:", type(records), len(records))
    print(records[0])
