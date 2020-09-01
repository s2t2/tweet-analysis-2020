


import re

from app.bot_communities.tokenizers import Tokenizer, SpacyTokenizer, ALPHANUMERIC_PATTERN, TWITTER_ALPHANUMERIC_PATTERN

def test_string_cleaning_keeps_tags_and_handles():
    status_text = "#HELLO @you http://hello.you ya know?"
    assert re.sub(ALPHANUMERIC_PATTERN, "", status_text) == 'HELLO you httphelloyou ya know'
    assert re.sub(TWITTER_ALPHANUMERIC_PATTERN, "", status_text) == '#HELLO @you httphelloyou ya know'

def test_tokenizers():
    tokenizer = Tokenizer()
    spacy_tokenizer = SpacyTokenizer()

    status_text = "Welcome to New York. Welcoming isn't it? :-D"
    assert tokenizer.basic_tokens(status_text) == ['welcome', 'new', 'york', 'welcoming']
    assert tokenizer.porter_stems(status_text) == ['welcom', 'new', 'york', 'welcom']
    assert tokenizer.custom_stems(status_text) == ['welcome', 'new', 'york', 'welcoming']
    assert spacy_tokenizer.custom_stem_lemmas(status_text) == ['welcome', 'new', 'york', 'welcome']
    assert [t.text for t in spacy_tokenizer.entity_tokens(status_text)] == ["New York"]

    status_text = "#HELLO #HELLO, #HELLO. #HELLO; #hello are you there? lol www.yo.com/#message"
    assert tokenizer.hashtags(status_text) == ["#HELLO", "#HELLO", "#HELLO", "#HELLO", "#HELLO"]

    status_text = "come @me bro"
    assert tokenizer.handles(status_text) == ["@ME"]
