
#
# adapted from: https://github.com/unitaryai/detoxify/blob/master/detoxify/detoxify.py
#
# 1) let's try different / lighter torch requirement approaches (to enable installation on heroku) - see requirements.txt file
# 2) let's also try to return the raw scores (to save processing time)
#
# references:
#   https://github.com/unitaryai/detoxify/blob/master/detoxify/detoxify.py
#   https://pytorch.org/docs/stable/hub.html
#   https://pytorch.org/docs/stable/hub.html#torch.hub.load_state_dict_from_url
#   https://pytorch.org/docs/stable/generated/torch.no_grad.html
#

from pprint import pprint

import torch
import transformers

CHECKPOINTS = {
    "original": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_original-c1212f89.ckpt",
    "unbiased": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_bias-4e693588.ckpt",
    "multilingual": "https://github.com/unitaryai/detoxify/releases/download/v0.1-alpha/toxic_multilingual-bbddc277.ckpt",
    "original-small": "https://github.com/unitaryai/detoxify/releases/download/v0.1.2/original-albert-0e1d6498.ckpt",
    "unbiased-small": "https://github.com/unitaryai/detoxify/releases/download/v0.1.2/unbiased-albert-c8519128.ckpt"
}

@torch.no_grad()
def predict_scores(text, model, tokenizer, class_names):
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(model.device)
    out = model(**inputs)[0]
    scores = torch.sigmoid(out).cpu().detach().numpy()
    return scores


if __name__ == '__main__':


    model_state = torch.hub.load_state_dict_from_url(CHECKPOINTS["original"], map_location="cpu")

    state_dict = model_state["state_dict"]

    config = model_state["config"]
    tokenizer_name = config["arch"]["args"]["tokenizer_name"] #> BertTokenizer
    model_name = config["arch"]["args"]["model_name"] #> BertForSequenceClassification
    model_type = config["arch"]["args"]["model_type"] #> bert-base-uncased
    num_classes = config["arch"]["args"]["num_classes"] #> 6
    class_names = config["dataset"]["args"]["classes"]

    print("---------------------------")
    print("MODEL TYPE:", model_type)
    print("MODEL NAME:", model_name)
    print("TOKENIZER NAME:", tokenizer_name)
    print(f"CLASS NAMES ({num_classes}):", class_names)

    # assert list(state_dict.keys()) == []
    assert tokenizer_name == "BertTokenizer"
    assert model_name == "BertForSequenceClassification"
    assert model_type == "bert-base-uncased"
    assert class_names == ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
    assert num_classes == 6


    print("---------------------------")

    model = getattr(transformers, model_name).from_pretrained(
        pretrained_model_name_or_path=None,
        config=model_type,
        num_labels=num_classes,
        state_dict=state_dict,
    )
    print("MODEL:", type(model))

    tokenizer = getattr(transformers, tokenizer_name).from_pretrained(model_type)
    print("TOKENIZER:", type(tokenizer))







    texts = [
        "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…",
        "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…",
    ]


    scores = predict_scores(texts, model, tokenizer, class_names)
    print("------------")
    print("SCORES:", type(scores), scores.shape, scores[0])

    results = []
    for score_index, score_row in enumerate(scores):
        #print(score_row)
        result = {}
        result["text"] = texts[score_index]
        for class_index, class_name in enumerate(class_names):
            result[class_name] = score_row[class_index]

        print("----")
        print(result)
        results.append(result)
