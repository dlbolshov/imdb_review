from django.shortcuts import render
from pathlib import Path
from scipy.special import softmax
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from django.core.cache import cache

def _get_models():
    BASE_DIR = Path(__file__).resolve().parent.parent
    tokenizer = cache.get('tokenizer')
    model = cache.get('model')
    if not tokenizer or not model:
        tokenizer = DistilBertTokenizer.from_pretrained(BASE_DIR / "models/model_nlp")
        model = DistilBertForSequenceClassification.from_pretrained(BASE_DIR / "models/model_nlp")
        cache.set('tokenizer', tokenizer, timeout=None)
        cache.set('model', model, timeout=None)
    return tokenizer, model

def index(request):
    return render(request, "base.html", {"prediction": "None"})


def prediction(request):
    tokenizer, model = _get_models()
    id2labels = {0:1, 1:2, 2:3, 3:4, 4:7, 5:8, 6:9, 7:10}
    message = request.POST["usermsg"]
    message = message.replace('<br /><br />', '\n')
    encoded = tokenizer(message, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
    logits = model(**encoded).logits[0].detach().numpy()
    pred = round(sum([id2labels[i] * w for i, w in enumerate(softmax(logits))]))
    pred_bin = 'positive' if pred > 5 else 'negative'
    return render(request, "base.html", {"prediction": pred, "prediction_bin": pred_bin})
