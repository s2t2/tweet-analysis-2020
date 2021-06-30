
from app.toxicity.scorer import ToxicityScorer

def test_toxicity_scorer():
    scorer = ToxicityScorer() # todo: use fixture

    assert scorer.model.class_names == [
        'toxicity',
        'severe_toxicity',
        'obscene',
        'threat',
        'insult',
        'identity_hate'
    ]

    #assert scorer.scores_table_column_names == [
    #    'status_text_id',
    #    'toxicity',
    #    'severe_toxicity',
    #    'obscene',
    #    'threat',
    #    'insult',
    #    'identity_hate'
    #]
