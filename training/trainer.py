"""
trainer.py - Final stable version
Key fix: load model in float32 first, then move to GPU
This prevents NaN gradients in DeBERTa-v3 disentangled attention on RTX 30xx GPUs
"""

import os, sys, argparse, torch, numpy as np, pandas as pd
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer, EarlyStoppingCallback)
from datasets import Dataset
from sklearn.metrics import f1_score, accuracy_score
import math

MODEL_NAME = "microsoft/deberta-v3-small"
MAX_LEN    = 128

BASE_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PROCESSED  = os.path.join(BASE_DIR, 'data', 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'training', 'saved_models')

HF_TOKEN = ""
HF_USER  = ""

LABEL_MAP = {
    "politeness": 2, "tone": 3, "intent": 3,
    "pa": 2, "sarcasm": 2, "urgency": 3, "power": 3,
}

def load_datasets(task_name):
    train_path = os.path.join(PROCESSED, f"{task_name}_train.csv")
    val_path   = os.path.join(PROCESSED, f"{task_name}_val.csv")
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Not found: {train_path}")
    if not os.path.exists(val_path):
        raise FileNotFoundError(f"Not found: {val_path}")
    train_df = pd.read_csv(train_path)[['text','label']].dropna()
    val_df   = pd.read_csv(val_path)[['text','label']].dropna()
    train_df['label'] = train_df['label'].astype(int)
    val_df['label']   = val_df['label'].astype(int)
    print(f"  Train: {len(train_df)} rows | Val: {len(val_df)} rows")
    print(f"  Label dist: {train_df['label'].value_counts().to_dict()}")
    return Dataset.from_pandas(train_df), Dataset.from_pandas(val_df)

def tokenize(ds, tokenizer):
    return ds.map(
        lambda b: tokenizer(b['text'], truncation=True,
                            padding='max_length', max_length=MAX_LEN),
        batched=True
    )

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": round(accuracy_score(labels, preds), 4),
        "f1":       round(f1_score(labels, preds, average='weighted'), 4),
    }

def calculate_warmup_steps(num_train_samples, batch_size, num_epochs, warmup_ratio=0.1):
    steps_per_epoch = math.ceil(num_train_samples / batch_size)
    total_steps     = steps_per_epoch * num_epochs
    warmup_steps    = max(1, int(total_steps * warmup_ratio))
    print(f"  Total steps: {total_steps} | Warmup steps: {warmup_steps} (ratio=0.1)")
    return warmup_steps

def train_model(task_name, num_labels):
    print(f"\n{'='*60}")
    print(f" Training: {task_name.upper()}  |  Labels: {num_labels}")
    print(f"{'='*60}")

    use_gpu    = torch.cuda.is_available()
    device     = "cuda" if use_gpu else "cpu"
    batch_size = 8 if use_gpu else 4

    if use_gpu:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem  = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  Device: {gpu_name} ({gpu_mem:.1f}GB)")
    else:
        print(f"  Device: CPU")

    output_dir = os.path.join(MODELS_DIR, task_name)
    os.makedirs(output_dir, exist_ok=True)

    num_epochs = 4

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("Loading and tokenizing datasets...")
    train_ds, val_ds = load_datasets(task_name)
    num_train = len(train_ds)
    train_ds  = tokenize(train_ds, tokenizer)
    val_ds    = tokenize(val_ds,   tokenizer)

    print("Loading model in float32...")
    # KEY FIX: always load in float32 first — prevents NaN in DeBERTa-v3 attention
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        ignore_mismatched_sizes=True,
        dtype=torch.float32,   # force float32 on load
    )

    # Initialize classifier weights properly to prevent NaN
    if hasattr(model, 'classifier'):
        torch.nn.init.xavier_uniform_(model.classifier.weight)
        torch.nn.init.zeros_(model.classifier.bias)
    if hasattr(model, 'pooler'):
        torch.nn.init.xavier_uniform_(model.pooler.dense.weight)
        torch.nn.init.zeros_(model.pooler.dense.bias)

    warmup_steps = calculate_warmup_steps(num_train, batch_size, num_epochs)

    import transformers as tf_mod
    tf_ver      = tuple(int(x) for x in tf_mod.__version__.split(".")[:2])
    use_new_api = tf_ver >= (4, 36)
    print(f"  Transformers {tf_mod.__version__}")

    common = dict(
        output_dir                  = output_dir,
        save_strategy               = "epoch",
        learning_rate               = 2e-5,
        per_device_train_batch_size = batch_size,
        per_device_eval_batch_size  = batch_size * 2,
        num_train_epochs            = num_epochs,
        weight_decay                = 0.01,
        load_best_model_at_end      = True,
        metric_for_best_model       = "f1",
        logging_steps               = 50,
        warmup_steps                = warmup_steps,
        fp16                        = False,
        bf16                        = False,
        report_to                   = "none",
        save_total_limit            = 1,
        max_grad_norm               = 1.0,
        use_cpu                     = not use_gpu,
        dataloader_pin_memory       = use_gpu,
    )

    if use_new_api:
        common["eval_strategy"] = "epoch"
    else:
        common["evaluation_strategy"] = "epoch"

    args    = TrainingArguments(**common)
    trainer = Trainer(
        model           = model,
        args            = args,
        train_dataset   = train_ds,
        eval_dataset    = val_ds,
        compute_metrics = compute_metrics,
        callbacks       = [EarlyStoppingCallback(early_stopping_patience=2)],
    )

    print("\nTraining started...")
    print("Watch for loss decreasing and grad_norm showing real numbers (not nan)")
    trainer.train()

    print("\nEvaluating...")
    results = trainer.evaluate()
    print(f"\nResults for {task_name}:")
    print(f"  Accuracy : {results.get('eval_accuracy', 'N/A')}")
    print(f"  F1 Score : {results.get('eval_f1', 'N/A')}")

    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved locally: {output_dir}")

    if HF_TOKEN and HF_USER:
        hf_repo = f"{HF_USER}/email-{task_name}"
        print(f"Pushing to HuggingFace: {hf_repo}")
        try:
            trainer.model.push_to_hub(hf_repo, token=HF_TOKEN)
            tokenizer.push_to_hub(hf_repo, token=HF_TOKEN)
            print(f"Pushed: https://huggingface.co/{hf_repo}")
        except Exception as e:
            print(f"Push failed (saved locally): {e}")
    else:
        print("HF_TOKEN/HF_USER not set — saved locally only.")

    return results

def train_all():
    tasks = [
        {"name": "power",      "num_labels": 3},
        {"name": "urgency",    "num_labels": 3},
        {"name": "intent",     "num_labels": 3},
        {"name": "tone",       "num_labels": 3},
        {"name": "sarcasm",    "num_labels": 2},
        {"name": "politeness", "num_labels": 2},
    ]
    summary = {}
    for t in tasks:
        try:
            r = train_model(t["name"], t["num_labels"])
            summary[t["name"]] = r
        except Exception as e:
            print(f"\nERROR training {t['name']}: {e}")
            summary[t["name"]] = {"error": str(e)}

    print("\n" + "="*60)
    print(" ALL TRAINING COMPLETE — Summary")
    print("="*60)
    for name, r in summary.items():
        if "error" in r:
            print(f"  {name:12} ERROR: {r['error']}")
        else:
            print(f"  {name:12} F1={r.get('eval_f1','?')} Acc={r.get('eval_accuracy','?')}")

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, '.env'))
        HF_TOKEN = os.getenv("HF_TOKEN", "")
        HF_USER  = os.getenv("HF_USER",  "")
    except ImportError:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="all",
        help="power | urgency | pa | intent | tone | sarcasm | politeness | all")
    parser.add_argument("--num_labels", type=int, default=None)
    a = parser.parse_args()

    if a.task == "all":
        train_all()
    else:
        if a.task not in LABEL_MAP:
            print(f"Unknown task. Choose: {list(LABEL_MAP.keys())} or all")
            sys.exit(1)
        train_model(a.task, a.num_labels or LABEL_MAP[a.task])