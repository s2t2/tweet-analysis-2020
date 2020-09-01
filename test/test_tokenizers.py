



from app.bot_communities.tokenizers import Tokenizer, SpacyTokenizer

def test_tokenizers():
    tokenizer = Tokenizer()
    spacy_tokenizer = SpacyTokenizer()

    status_text = "Welcome to New York. Welcoming isn't it? :-D"
    assert tokenizer.basic_tokens(status_text) == ['welcome', 'new', 'york', 'welcoming']
    assert tokenizer.porter_stems(status_text) == ['welcom', 'new', 'york', 'welcom']
    assert tokenizer.custom_stems(status_text) == ['welcome', 'new', 'york', 'welcoming']
    assert spacy_tokenizer.custom_stem_lemmas(status_text) == ['welcome', 'new', 'york', 'welcome']
    assert [t.text for t in spacy_tokenizer.entity_tokens(status_text)] == ["New York"]

    # status_text = ""
    # ...
    # ...
