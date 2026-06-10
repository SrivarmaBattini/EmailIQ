"""
tone_prep.py
Prepares tone training data from GoEmotions dataset.
Maps 28 emotions → 3 tone classes:
  aggressive  (0): anger, annoyance, disapproval, disgust
  frustrated  (1): sadness, disappointment, grief, remorse, fear, nervousness, embarrassment
  professional(2): everything else (joy, neutral, approval, etc.)
Output: data/processed/tone_train.csv, tone_val.csv
"""

import pandas as pd
import os
import re
import json
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'tone', 'goemotion', 'data')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

AGGRESSIVE  = {'anger', 'annoyance', 'disapproval', 'disgust'}
FRUSTRATED  = {'sadness', 'disappointment', 'grief', 'remorse', 'fear', 'nervousness', 'embarrassment'}
# Everything else maps to professional

def load_emotions_list():
    path = os.path.join(RAW, 'emotions.txt')
    if not os.path.exists(path):
        # fallback hardcoded list
        return ['admiration','amusement','anger','annoyance','approval','caring','confusion',
                'curiosity','desire','disappointment','disapproval','disgust','embarrassment',
                'excitement','fear','gratitude','grief','joy','love','nervousness','optimism',
                'pride','realization','relief','remorse','sadness','surprise','neutral']
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def emotion_id_to_tone(emotion_id, emotions_list):
    try:
        idx = int(emotion_id)
        emotion = emotions_list[idx]
    except:
        return None
    if emotion in AGGRESSIVE:
        return 0
    elif emotion in FRUSTRATED:
        return 1
    else:
        return 2

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text).strip()[:512]

def load_split(filename, emotions_list):
    path = os.path.join(RAW, filename)
    if not os.path.exists(path):
        print(f"[SKIP] {path} not found")
        return pd.DataFrame()
    print(f"Loading {filename} ...")
    df = pd.read_csv(path, sep='\t', header=None)
    # col 0 = text, col 1 = emotion_ids (comma-separated), col 2 = id
    records = []
    for _, row in df.iterrows():
        text = clean_text(str(row[0]))
        if len(text) < 5:
            continue
        # emotion_ids can be comma separated (multi-label) — take first
        emotion_ids = str(row[1]).split(',')
        label = emotion_id_to_tone(emotion_ids[0].strip(), emotions_list)
        if label is not None:
            records.append({'text': text, 'label': label})
    result = pd.DataFrame(records)
    print(f"  Loaded {len(result)} rows. Label dist: {result['label'].value_counts().to_dict()}")
    return result

def main():
    emotions_list = load_emotions_list()
    print(f"Loaded {len(emotions_list)} emotion labels")

    train_df = load_split('train.tsv', emotions_list)
    val_df   = load_split('dev.tsv',   emotions_list)
    test_df  = load_split('test.tsv',  emotions_list)

    if len(train_df) == 0:
        print("ERROR: No tone data loaded.")
        return

    # Balance training data — cap each class
    parts = []
    for label in [0, 1, 2]:
        subset = train_df[train_df['label'] == label]
        cap = min(15000, len(subset))
        parts.append(subset.sample(cap, random_state=42))
    balanced_train = pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)

    if len(val_df) == 0:
        balanced_train, val_df = train_test_split(balanced_train, test_size=0.1, random_state=42)

    balanced_train.to_csv(os.path.join(OUT, 'tone_train.csv'), index=False)
    val_df.to_csv(os.path.join(OUT,   'tone_val.csv'),   index=False)
    print(f"\nSaved: tone_train.csv ({len(balanced_train)} rows), tone_val.csv ({len(val_df)} rows)")
    print(f"Train labels: {balanced_train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
