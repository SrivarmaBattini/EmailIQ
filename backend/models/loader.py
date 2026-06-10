"""
loader.py - Loads all 7 DeBERTa models from HuggingFace Hub at startup.
Falls back to microsoft/deberta-v3-small if custom model not found.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN   = os.getenv("HF_TOKEN", "")
HF_USER    = os.getenv("HF_USER", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"
BASE_MODEL = "microsoft/deberta-v3-small"

TASK_CONFIG = {
    "politeness": {"num_labels": 2, "labels": ["impolite", "polite"]},
    "tone":       {"num_labels": 3, "labels": ["aggressive", "frustrated", "professional"]},
    "intent":     {"num_labels": 3, "labels": ["request", "complaint", "follow-up"]},
    "pa":         {"num_labels": 2, "labels": ["neutral", "passive_aggressive"]},
    "sarcasm":    {"num_labels": 2, "labels": ["neutral", "sarcastic"]},
    "urgency":    {"num_labels": 3, "labels": ["low", "medium", "high"]},
    "power":      {"num_labels": 3, "labels": ["upward", "peer", "downward"]},
}

_models    = {}
_tokenizer = None

# def get_model_id(task: str) -> str:
#     if HF_USER:
#         return f"{HF_USER}/email-{task}"
#     return BASE_MODEL

def get_model_id(task: str) -> str:
    if ENVIRONMENT == "local":
        local_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'training', 'saved_models', task
        ))
        if os.path.exists(local_path):
            print(f"  [LOCAL ENV] Loading {task} from fast local path")
            return local_path

    if HF_USER:
        return f"{HF_USER}/email-{task}"
    return BASE_MODEL
    
def load_all_models():
    global _tokenizer, _models
    print(f"Loading models on device: {DEVICE}")
    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    for task, cfg in TASK_CONFIG.items():
        model_id = get_model_id(task)
        try:
            print(f"  Loading {task} from {model_id}...")
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id,
                num_labels=cfg["num_labels"],
                token=HF_TOKEN if HF_TOKEN else None,
                ignore_mismatched_sizes=True,
            )
        except Exception as e:
            print(f"  Falling back to base model for {task}: {e}")
            model = AutoModelForSequenceClassification.from_pretrained(
                BASE_MODEL,
                num_labels=cfg["num_labels"],
                ignore_mismatched_sizes=True,
            )
        model.eval()
        model.to(DEVICE)
        _models[task] = model
    print("All models loaded.")

def get_models():
    return _models, _tokenizer, DEVICE

def get_task_labels(task: str):
    return TASK_CONFIG[task]["labels"]
