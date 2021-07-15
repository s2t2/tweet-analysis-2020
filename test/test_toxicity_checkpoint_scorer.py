
from app.toxicity.checkpoint_scorer import ToxicityScorer
from app.toxicity.model_manager import ModelManager
from conftest import toxicity_texts

def test_toxicity_scorer(original_model_manager):
    # the different models have different class names
    # so we need different table structures to store the resulting scores

    original = ToxicityScorer(model_manager=original_model_manager)
    assert original.mgr.model_name == "BertForSequenceClassification"
    assert original.mgr.model_type == "bert-base-uncased"
    assert original.mgr.class_names == [
        'toxicity',
        'severe_toxicity',
        'obscene',
        'threat',
        'insult',
        'identity_hate'
    ]

    scores = original.predict(toxicity_texts)
    assert scores[0].tolist() == [0.12640126049518585, 0.00022532008006237447, 0.0018298450158908963, 0.0005070280167274177, 0.009287197142839432, 0.0018323149997740984]
    assert scores[1].tolist() == [0.0008546802564524114, 0.00011462702241260558, 0.00016588227299507707, 0.00013761487207375467, 0.0001857876923168078, 0.00015746793360449374]
