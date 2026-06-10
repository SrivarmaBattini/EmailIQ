"""
politeness_prep.py
Prepares politeness training data from:
1. politeness/politeness/politeness.tsv  (P_0 to P_9 scale)
2. politeness/jigsaw/train.csv           (toxic/non-toxic)
3. politeness/stanford/test.csv          (human annotated, used as val)
Output: data/processed/politeness_train.csv, politeness_val.csv
"""

import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'politeness')
OUT  = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'http\S+', '', text)
    return text[:512]

def load_politeness_tsv():
    path = os.path.join(RAW, 'politeness', 'politeness.tsv')
    if not os.path.exists(path):
        print(f"[SKIP] {path} not found")
        return pd.DataFrame()
    print("Loading politeness.tsv ...")
    df = pd.read_csv(path, sep='\t')
    # P_0 to P_4 = impolite, P_5 to P_9 = polite
    style_map = {
        'P_0': 0, 'P_1': 0, 'P_2': 0, 'P_3': 0, 'P_4': 0,
        'P_5': 1, 'P_6': 1, 'P_7': 1, 'P_8': 1, 'P_9': 1,
    }
    df = df[df['style'].isin(style_map.keys())].copy()
    df['label'] = df['style'].map(style_map)
    df['text']  = df['txt'].apply(clean_text)
    df = df[df['text'].str.len() > 10][['text', 'label']]
    print(f"  Loaded {len(df)} rows. Label dist: {df['label'].value_counts().to_dict()}")
    return df

def load_jigsaw():
    path = os.path.join(RAW, 'jigsaw', 'jigsaw_train.csv')
    if not os.path.exists(path):
        path = os.path.join(RAW, 'jigsaw', 'train.csv')
    if not os.path.exists(path):
        print(f"[SKIP] jigsaw train.csv not found")
        return pd.DataFrame()
    print("Loading jigsaw ...")
    df = pd.read_csv(path)
    df['label'] = df['toxic'].apply(lambda x: 0 if x == 1 else 1)  # toxic=impolite(0), non-toxic=polite(1)
    df['text']  = df['comment_text'].apply(clean_text)
    df = df[df['text'].str.len() > 10][['text', 'label']]
    print(f"  Loaded {len(df)} rows. Label dist: {df['label'].value_counts().to_dict()}")
    return df

def load_stanford():
    path = os.path.join(RAW, 'stanford', 'stanford_test.csv')
    if not os.path.exists(path):
        path = os.path.join(RAW, 'stanford', 'test.csv')
    if not os.path.exists(path):
        print(f"[SKIP] stanford test.csv not found")
        return pd.DataFrame()
    print("Loading stanford ...")
    df = pd.read_csv(path)
    df['text']  = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 10][['text', 'label']]
    print(f"  Loaded {len(df)} rows. Label dist: {df['label'].value_counts().to_dict()}")
    return df

def main():
    parts = []
    pol_df = load_politeness_tsv()
    if len(pol_df): parts.append(pol_df)

    jig_df = load_jigsaw()
    if len(jig_df): parts.append(jig_df)

    if not parts:
        print("ERROR: No data loaded. Check file paths.")
        return

    combined = pd.concat(parts, ignore_index=True).dropna().drop_duplicates(subset=['text'])
    combined = combined[combined['text'].str.len() > 10]

    # Balance classes — cap at 200k each
    polite   = combined[combined['label'] == 1].sample(min(200000, len(combined[combined['label']==1])), random_state=42)
    impolite = combined[combined['label'] == 0].sample(min(200000, len(combined[combined['label']==0])), random_state=42)
    balanced = pd.concat([polite, impolite]).sample(frac=1, random_state=42).reset_index(drop=True)

    train, val = train_test_split(balanced, test_size=0.1, random_state=42, stratify=balanced['label'])

    # Add stanford as extra val if available
    stan_df = load_stanford()
    if len(stan_df):
        val = pd.concat([val, stan_df]).drop_duplicates(subset=['text']).reset_index(drop=True)

    train.to_csv(os.path.join(OUT, 'politeness_train.csv'), index=False)
    val.to_csv(os.path.join(OUT, 'politeness_val.csv'), index=False)
    print(f"\nSaved: politeness_train.csv ({len(train)} rows), politeness_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
