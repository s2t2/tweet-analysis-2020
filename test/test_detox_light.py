from detoxify import Detoxify
import numpy as np
from transformers import BertForSequenceClassification, BertTokenizer
from pandas import DataFrame

import pytest

from app.toxicity.detox_light import ModelManager

@pytest.fixture(scope="module")
def original_model_manager():
    mgr = ModelManager(checkpoint_name="original")
    mgr.load_model_state()
    return mgr


texts = [
    "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
    "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
]

def test_original_model(original_model_manager):
    mgr = original_model_manager
    assert mgr.tokenizer_name == "BertTokenizer"
    assert mgr.model_name == "BertForSequenceClassification"
    assert mgr.model_type == "bert-base-uncased"
    assert mgr.class_names == ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
    assert mgr.num_classes == 6
    assert isinstance(mgr.model, BertForSequenceClassification)
    assert isinstance(mgr.tokenizer, BertTokenizer)

    scores = mgr.predict_scores(texts)
    assert isinstance(scores, np.ndarray)
    assert scores.shape == (2, 6)
    assert scores[0].tolist() == [0.12640126049518585, 0.00022532008006237447, 0.0018298450158908963, 0.0005070280167274177, 0.009287197142839432, 0.0018323149997740984]
    assert scores[1].tolist() == [0.0008546802564524114, 0.00011462702241260558, 0.00016588227299507707, 0.00013761487207375467, 0.0001857876923168078, 0.00015746793360449374]

    records = mgr.predict_records(texts)
    assert records == [
        {
            'text': 'RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…',
            'toxicity': 0.12640126049518585, 'severe_toxicity': 0.00022532008006237447, 'obscene': 0.0018298450158908963, 'threat': 0.0005070280167274177, 'insult': 0.009287197142839432, 'identity_hate': 0.0018323149997740984
        }, {
            'text': 'RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…',
            'toxicity': 0.0008546802564524114, 'severe_toxicity': 0.00011462702241260558, 'obscene': 0.00016588227299507707, 'threat': 0.00013761487207375467, 'insult': 0.0001857876923168078, 'identity_hate': 0.00015746793360449374
        }
    ]

    df = mgr.predict_df(records)
    assert isinstance(df, DataFrame)


def test_provided_model():
    model = Detoxify("original")
    results = model.predict(texts)
    assert results == {
        'toxicity': [0.12640126049518585, 0.0008546802564524114],
        'severe_toxicity': [0.00022532008006237447, 0.00011462702241260558],
        'obscene': [0.0018298450158908963, 0.00016588227299507707],
        'threat': [0.0005070280167274177, 0.00013761487207375467],
        'insult': [0.009287197142839432, 0.0001857876923168078],
        'identity_hate': [0.0018323149997740984, 0.00015746793360449374]
    }
