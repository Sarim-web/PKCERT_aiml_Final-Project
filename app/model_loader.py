import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "incident_severity_final"

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None
_tokenizer = None
_id2label = None

def get_model():
    global _model, _tokenizer, _id2label
    if _model is None:
        _tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
        _model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
        _model.to(_device)
        _model.eval()
        _id2label = _model.config.id2label
    return _model, _tokenizer, _id2label, _device

def predict_severity(text: str) -> dict:
    model, tokenizer, id2label, device = get_model()
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=True
    ).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        pred_id = int(probs.argmax().item())
        confidence = float(probs[pred_id].item())
    return {
        "severity": id2label[pred_id],
        "confidence": round(confidence, 4),
        "label_id": pred_id
    }