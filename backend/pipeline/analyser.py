"""
analyser.py - Runs all 7 DeBERTa models in parallel and returns results.
"""
import torch
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from backend.models.loader import get_models, get_task_labels

MAX_LEN = 128

def predict_single(task: str, text: str) -> dict:
    models, tokenizer, device = get_models()
    model = models.get(task)
    if model is None:
        return {"label": "unknown", "confidence": 0.0, "scores": {}}

    labels = get_task_labels(task)
    inputs = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN,
        return_tensors="pt"
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs   = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().numpy()

    pred_idx    = int(np.argmax(probs))
    confidence  = float(probs[pred_idx])
    label       = labels[pred_idx]
    scores      = {labels[i]: round(float(probs[i]), 4) for i in range(len(labels))}

    return {"label": label, "confidence": round(confidence, 4), "scores": scores}

def analyse_email(text: str) -> dict:
    """Run all 7 classifiers in parallel and return combined results."""
    tasks = ["politeness", "tone", "intent", "pa", "sarcasm", "urgency", "power"]

    results = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {task: executor.submit(predict_single, task, text) for task in tasks}
        for task, future in futures.items():
            try:
                results[task] = future.result(timeout=30)
            except Exception as e:
                results[task] = {"label": "unknown", "confidence": 0.0, "scores": {}, "error": str(e)}

    return results
