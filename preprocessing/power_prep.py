"""
power_prep.py
Labels: 0=upward, 1=peer, 2=downward
Output: data/processed/power_train.csv, power_val.csv
"""

import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'combined')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

UPWARD_PATTERNS   = [r'\bi wanted to check\b', r'\bwould it be possible\b',
                     r'\bi hope you don\'t mind\b', r'\bplease advise\b',
                     r'\bi was wondering if\b', r'\bi just wanted to\b',
                     r'\bwith your permission\b', r'\bat your convenience\b',
                     r'\bwould you be available\b', r'\bi appreciate your time\b']
DOWNWARD_PATTERNS = [r'\bplease ensure\b', r'\bi need you to\b', r'\bmake sure\b',
                     r'\bi expect\b', r'\byou should\b', r'\bi require\b',
                     r'\bby end of day\b', r'\bimmediately\b', r'\bi am instructing\b',
                     r'\bthis is mandatory\b']

def clean_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r'\s+', ' ', text).strip()[:512]

def rule_power(text):
    t = text.lower()
    up_score   = sum(1 for p in UPWARD_PATTERNS   if re.search(p, t))
    down_score = sum(1 for p in DOWNWARD_PATTERNS if re.search(p, t))
    if up_score > down_score and up_score > 0:   return 0
    if down_score > up_score and down_score > 0: return 2
    return 1

def main():
    path = os.path.join(RAW, 'final_dataset.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        return

    print("Loading final_dataset.csv for power dynamic ...")
    df = pd.read_csv(path, usecols=['text', 'power_dynamic'])
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 10].dropna()

    label_map = {'upward': 0, 'peer': 1, 'downward': 2}
    df['label'] = df['power_dynamic'].map(label_map)
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)

    # Augment with rule-based labeling
    peer_df = df[df['label'] == 1].copy()
    rule_labeled = peer_df.copy()
    rule_labeled['label'] = rule_labeled['text'].apply(rule_power)

    extra_up   = rule_labeled[rule_labeled['label'] == 0]
    extra_down = rule_labeled[rule_labeled['label'] == 2]

    upward_df   = pd.concat([df[df['label']==0], extra_up])
    downward_df = pd.concat([df[df['label']==2], extra_down])
    peer_final  = df[df['label']==1]

    cap = min(5000, len(upward_df), len(downward_df), len(peer_final))
    balanced = pd.concat([
        upward_df.sample(cap, random_state=42),
        downward_df.sample(cap, random_state=42),
        peer_final.sample(cap, random_state=42),
    ])[['text', 'label']].sample(frac=1, random_state=42).reset_index(drop=True)

    train, val = train_test_split(balanced, test_size=0.1, random_state=42, stratify=balanced['label'])
    train.to_csv(os.path.join(OUT, 'power_train.csv'), index=False)
    val.to_csv(os.path.join(OUT,   'power_val.csv'),   index=False)
    print(f"Saved: power_train.csv ({len(train)} rows), power_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
