"""
intent_prep.py
Generates intent labels from Enron email corpus using rule-based labeling.
Intent classes:
  0 = request
  1 = complaint
  2 = follow-up
Output: data/processed/intent_train.csv, intent_val.csv
"""

import pandas as pd
import os
import re
import email
from sklearn.model_selection import train_test_split

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'enron')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT, exist_ok=True)

REQUEST_PATTERNS = [
    r'\bcould you\b', r'\bplease\b', r'\bcan you\b', r'\bwould you\b',
    r'\bkindly\b', r'\bi would like\b', r'\bi need you to\b',
    r'\bwould it be possible\b', r'\bplease provide\b', r'\bplease send\b',
    r'\bplease confirm\b', r'\bplease let me know\b', r'\bi am requesting\b',
    r'\bwould appreciate\b', r'\bcan we\b', r'\bwould you mind\b'
]

COMPLAINT_PATTERNS = [
    r'\bissue\b', r'\bproblem\b', r'\bnot working\b', r'\bdisappointed\b',
    r'\bcomplaint\b', r'\bfailed\b', r'\berror\b', r'\bincorrect\b',
    r'\bunacceptable\b', r'\bconcerned\b', r'\bfrustrated\b', r'\bwrong\b',
    r'\binaccurate\b', r'\boverlook\b', r'\bnot received\b', r'\bstill waiting\b',
    r'\bno response\b', r'\bmistake\b', r'\bserious concern\b'
]

FOLLOWUP_PATTERNS = [
    r'\bfollowing up\b', r'\bcircling back\b', r'\bchecking in\b',
    r'\bany update\b', r'\bhaven\'t heard\b', r'\bjust wanted to check\b',
    r'\breminder\b', r'\bas discussed\b', r'\bper our conversation\b',
    r'\bto follow up\b', r'\bstatus update\b', r'\bwanted to follow\b',
    r'\bwaiting for\b', r'\bpending response\b', r'\bno reply\b'
]

def extract_email_body(raw_message):
    try:
        msg = email.message_from_string(raw_message)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True)
            if body:
                body = body.decode('utf-8', errors='ignore')
            else:
                body = str(msg.get_payload())
        return body.strip()
    except:
        return ""

def classify_intent(text):
    text_lower = text.lower()
    scores = {'request': 0, 'complaint': 0, 'follow-up': 0}
    for p in REQUEST_PATTERNS:
        if re.search(p, text_lower): scores['request'] += 1
    for p in COMPLAINT_PATTERNS:
        if re.search(p, text_lower): scores['complaint'] += 1
    for p in FOLLOWUP_PATTERNS:
        if re.search(p, text_lower): scores['follow-up'] += 1

    max_score = max(scores.values())
    if max_score == 0:
        return None  # ambiguous
    if list(scores.values()).count(max_score) > 1:
        return None  # tie — ambiguous

    winner = max(scores, key=scores.get)
    label_map = {'request': 0, 'complaint': 1, 'follow-up': 2}
    return label_map[winner]

def clean_body(text):
    if not isinstance(text, str): return ""
    # Remove forwarded headers
    text = re.sub(r'-{3,}.*?-{3,}', '', text, flags=re.DOTALL)
    text = re.sub(r'From:.*?\n', '', text)
    text = re.sub(r'To:.*?\n', '', text)
    text = re.sub(r'Subject:.*?\n', '', text)
    text = re.sub(r'Date:.*?\n', '', text)
    text = re.sub(r'Message-ID:.*?\n', '', text)
    text = re.sub(r'X-.*?:.*?\n', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:512]

def main():
    enron_path = os.path.join(RAW, 'emails.csv')
    if not os.path.exists(enron_path):
        print(f"ERROR: {enron_path} not found. Place emails.csv in data/raw/enron/")
        return

    print("Loading Enron emails (this may take a moment)...")
    # Load in chunks to manage memory
    records = []
    chunk_size = 10000
    target_per_class = 6000

    class_counts = {0: 0, 1: 0, 2: 0}

    for chunk in pd.read_csv(enron_path, chunksize=chunk_size, usecols=['message']):
        for _, row in chunk.iterrows():
            if all(v >= target_per_class for v in class_counts.values()):
                break
            body = extract_email_body(str(row['message']))
            body = clean_body(body)
            if len(body) < 30:
                continue
            label = classify_intent(body)
            if label is None:
                continue
            if class_counts[label] < target_per_class:
                records.append({'text': body, 'label': label})
                class_counts[label] += 1

        if all(v >= target_per_class for v in class_counts.values()):
            break

        print(f"  Progress: {class_counts}", end='\r')

    print(f"\nCollected: {class_counts}")
    df = pd.DataFrame(records).dropna().drop_duplicates(subset=['text'])
    train, val = train_test_split(df, test_size=0.1, random_state=42, stratify=df['label'])

    train.to_csv(os.path.join(OUT, 'intent_train.csv'), index=False)
    val.to_csv(os.path.join(OUT,   'intent_val.csv'),   index=False)
    print(f"Saved: intent_train.csv ({len(train)} rows), intent_val.csv ({len(val)} rows)")
    print(f"Train labels: {train['label'].value_counts().to_dict()}")

if __name__ == '__main__':
    main()
