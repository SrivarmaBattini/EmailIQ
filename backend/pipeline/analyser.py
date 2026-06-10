"""
analyser.py - Runs all 7 DeBERTa models in parallel via HuggingFace Serverless API.
"""
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_USER = os.getenv("HF_USER", "Srivarma11")

def predict_single(task: str, text: str) -> dict:
    if not HF_TOKEN:
        return {"label": "unknown", "confidence": 0.0, "scores": {}, "error": "Missing HF_TOKEN"}

    url = f"https://router.huggingface.co/hf-inference/models/{HF_USER}/email-{task}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": text}

    try:
        for attempt in range(5):
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 503:
                # Model is loading on HuggingFace servers, wait and retry
                time.sleep(2)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # The API returns a list of lists: [[{"label": "polite", "score": 0.99}, ...]]
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                predictions = data[0]
                best_pred = max(predictions, key=lambda x: x["score"])
                scores = {item["label"]: round(float(item["score"]), 4) for item in predictions}
                
                return {
                    "label": best_pred["label"],
                    "confidence": round(float(best_pred["score"]), 4),
                    "scores": scores
                }
            elif "error" in data:
                return {"label": "unknown", "confidence": 0.0, "scores": {}, "error": data["error"]}
            else:
                return {"label": "unknown", "confidence": 0.0, "scores": {}, "error": "Invalid API response format"}
        
        return {"label": "unknown", "confidence": 0.0, "scores": {}, "error": "Model timeout on HuggingFace"}
            
    except Exception as e:
        return {"label": "unknown", "confidence": 0.0, "scores": {}, "error": str(e)}

def analyse_email(text: str) -> dict:
    """Run all 7 classifiers in parallel via HuggingFace API and return combined results."""
    tasks = ["politeness", "tone", "intent", "pa", "sarcasm", "urgency", "power"]

    results = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {task: executor.submit(predict_single, task, text) for task in tasks}
        for task, future in futures.items():
            try:
                results[task] = future.result(timeout=45)
            except Exception as e:
                results[task] = {"label": "unknown", "confidence": 0.0, "scores": {}, "error": str(e)}

    return results
