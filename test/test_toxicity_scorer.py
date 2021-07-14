
from app.toxicity.scorer import ToxicityScorer

def test_toxicity_scorer():
    # the different models have different class names
    # so we need different table structures to store the resulting scores

    original = ToxicityScorer(model_name="original") # todo: use fixture
    assert original.model.class_names == [
        'toxicity',
        'severe_toxicity',
        'obscene',
        'threat',
        'insult',
        'identity_hate'
    ]

    unbiased = ToxicityScorer(model_name="unbiased") # todo: use fixture
    assert unbiased.model.class_names == [
        'toxicity',
        'severe_toxicity',
        'obscene',
        'identity_attack',
        'insult',
        'threat',
        'sexual_explicit'
    ]
