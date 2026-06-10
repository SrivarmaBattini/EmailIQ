"""
pa_prep.py
Prepares passive-aggression training data from final_dataset.csv.
Labels: 0 = neutral, 1 = passive_aggressive
Output: data/processed/pa_train.csv, pa_val.csv
"""

import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'combined')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

# Known PA phrases for augmentation labeling
PA_PHRASES = [
    "as per my last email", "as previously mentioned", "friendly reminder",
    "going forward", "as discussed", "per our conversation",
    "i imagine things must be very busy", "haven't heard back from you",
    "circling back", "just wanted to follow up again",
    "not sure if you saw my last message", "please advise",
    "i'll leave this with you", "as i mentioned before",
    "kindly revert", "do the needful", "hope this helps",
    "i trust this is clear", "as clearly stated",
    "i am surprised that", "i would have expected",
    "not sure how else to explain", "maybe i wasn't clear",
    "with all due respect", "no offence but",
    "i guess i'll just", "i suppose i have to"
]

def clean_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r'\s+', ' ', text).strip()[:512]

def has_pa_phrase(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in PA_PHRASES)

def main():
    path = os.path.join(RAW, 'final_dataset.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        return

    print("Loading final_dataset.csv ...")
    df = pd.read_csv(path, usecols=['text', 'passive_aggressive'])
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 10].dropna()

    df['label'] = df['passive_aggressive'].apply(
        lambda x: 1 if str(x).strip() == 'passive_aggressive' else 0
    )

    pa_df      = df[df['label'] == 1]
    neutral_df = df[df['label'] == 0]

    print(f"PA samples: {len(pa_df)}, Neutral samples: {len(neutral_df)}")

    # Augment PA using rule-based labeling on neutral samples
    print("Augmenting PA with rule-based labeling...")
    extra_pa = neutral_df[neutral_df['text'].apply(has_pa_phrase)].copy()
    extra_pa['label'] = 1
    print(f"Rule-based PA additions: {len(extra_pa)}")

    pa_combined = pd.concat([pa_df, extra_pa]).drop_duplicates(subset=['text'])
    neutral_sample = neutral_df[~neutral_df['text'].apply(has_pa_phrase)].sample(
        min(15000, len(neutral_df)), random_state=42
    )

    combined = pd.concat([pa_combined, neutral_sample])[['text', 'label']]
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    train, val = train_test_split(combined, test_size=0.1, random_state=42, stratify=combined['label'])

    train.to_csv(os.path.join(OUT, 'pa_train.csv'), index=False)
    val.to_csv(os.path.join(OUT,   'pa_val.csv'),   index=False)
    print(f"Saved: pa_train.csv ({len(train)} rows), pa_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
