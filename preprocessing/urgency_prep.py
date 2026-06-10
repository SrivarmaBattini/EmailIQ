"""
urgency_prep.py
Labels: 0=low, 1=medium, 2=high
Output: data/processed/urgency_train.csv, urgency_val.csv
"""

import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'combined')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

HIGH_PATTERNS   = [r'\basap\b', r'\burgent\b', r'\bimmediately\b', r'\beod\b',
                   r'\bend of day\b', r'\bdeadline today\b', r'\bright away\b',
                   r'\bcritical\b', r'\bemergency\b', r'\bno later than today\b']
MEDIUM_PATTERNS = [r'\bby end of week\b', r'\bsoon\b', r'\bby friday\b',
                   r'\bthis week\b', r'\bwhen you get a chance\b',
                   r'\bby tomorrow\b', r'\bnext day\b']

def clean_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r'\s+', ' ', text).strip()[:512]

def rule_urgency(text):
    t = text.lower()
    for p in HIGH_PATTERNS:
        if re.search(p, t): return 2
    for p in MEDIUM_PATTERNS:
        if re.search(p, t): return 1
    return 0

def main():
    path = os.path.join(RAW, 'final_dataset.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        return

    print("Loading final_dataset.csv for urgency ...")
    df = pd.read_csv(path, usecols=['text', 'urgency'])
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 10].dropna()

    label_map = {'low': 0, 'medium': 1, 'high': 2}
    df['label'] = df['urgency'].map(label_map)
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)

    # Augment low-class samples using rule labeling
    unlabeled = df[df['label'] == 0].copy()
    rule_relabeled = unlabeled.copy()
    rule_relabeled['label'] = rule_relabeled['text'].apply(rule_urgency)
    extra_high   = rule_relabeled[rule_relabeled['label'] == 2]
    extra_medium = rule_relabeled[rule_relabeled['label'] == 1]

    high_df   = pd.concat([df[df['label']==2], extra_high])
    medium_df = pd.concat([df[df['label']==1], extra_medium])
    low_df    = df[df['label']==0]

    # Balance
    cap = min(10000, len(high_df), len(medium_df), len(low_df))
    balanced = pd.concat([
        high_df.sample(cap, random_state=42),
        medium_df.sample(cap, random_state=42),
        low_df.sample(cap, random_state=42),
    ])[['text', 'label']].sample(frac=1, random_state=42).reset_index(drop=True)

    train, val = train_test_split(balanced, test_size=0.1, random_state=42, stratify=balanced['label'])
    train.to_csv(os.path.join(OUT, 'urgency_train.csv'), index=False)
    val.to_csv(os.path.join(OUT,   'urgency_val.csv'),   index=False)
    print(f"Saved: urgency_train.csv ({len(train)} rows), urgency_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
