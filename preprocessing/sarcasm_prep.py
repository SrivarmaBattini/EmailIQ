"""
sarcasm_prep.py
Prepares sarcasm training data from train-balanced-sarcasm.csv.
Labels: 0 = neutral, 1 = sarcastic
Output: data/processed/sarcasm_train.csv, sarcasm_val.csv
"""

import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'sarcasm')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:512]

def main():
    path = os.path.join(RAW, 'train-balanced-sarcasm.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        return

    print("Loading train-balanced-sarcasm.csv ...")
    df = pd.read_csv(path, usecols=['label', 'comment'])
    df.columns = ['label', 'text']
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 5].dropna()
    df = df.drop_duplicates(subset=['text'])

    print(f"Loaded {len(df)} rows. Label dist: {df['label'].value_counts().to_dict()}")

    # Already balanced — sample 100k each for faster training
    sarcastic = df[df['label'] == 1].sample(min(100000, len(df[df['label']==1])), random_state=42)
    neutral   = df[df['label'] == 0].sample(min(100000, len(df[df['label']==0])), random_state=42)
    balanced  = pd.concat([sarcastic, neutral]).sample(frac=1, random_state=42).reset_index(drop=True)

    train, val = train_test_split(balanced, test_size=0.1, random_state=42, stratify=balanced['label'])

    train.to_csv(os.path.join(OUT, 'sarcasm_train.csv'), index=False)
    val.to_csv(os.path.join(OUT,   'sarcasm_val.csv'),   index=False)
    print(f"Saved: sarcasm_train.csv ({len(train)} rows), sarcasm_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
