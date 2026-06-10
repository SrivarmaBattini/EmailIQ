"""
evaluate_pipeline.py
Evaluates the full pipeline on 500 sampled Enron emails.
Run: python evaluation/evaluate_pipeline.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import email as email_lib
import re
import requests
import json
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ENRON_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'enron', 'emails.csv')
OUT_PATH    = os.path.join(os.path.dirname(__file__), 'results', 'pipeline_results.csv')
N_SAMPLES   = 500

def extract_body(raw):
    try:
        msg  = email_lib.message_from_string(raw)
        body = msg.get_payload(decode=True)
        if body: return body.decode('utf-8', errors='ignore').strip()
        return str(msg.get_payload()).strip()
    except: return ""

def clean(text):
    text = re.sub(r'^(From|To|Date|Subject|Message-ID|X-\w+):.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:512]

def analyse(text):
    try:
        r = requests.post(f"{BACKEND_URL}/api/analyse",
            json={"email_text": text, "relationship": "peer"}, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    print(f"Loading Enron emails from {ENRON_PATH}...")

    df    = pd.read_csv(ENRON_PATH, nrows=5000, usecols=['message'])
    emails= []
    for _, row in df.iterrows():
        body = clean(extract_body(str(row['message'])))
        if len(body) > 50: emails.append(body)
        if len(emails) >= N_SAMPLES: break

    print(f"Sampled {len(emails)} emails. Running analysis...")
    records = []
    for i, text in enumerate(emails):
        result = analyse(text)
        if "error" in result:
            print(f"  [{i+1}] ERROR: {result['error']}")
            continue
        records.append({
            "email_preview": text[:80],
            "score":         result.get("score", {}).get("score", 0),
            "grade":         result.get("score", {}).get("grade", ""),
            "tone":          result.get("signals", {}).get("tone", {}).get("label", ""),
            "politeness":    result.get("signals", {}).get("politeness", {}).get("label", ""),
            "pa":            result.get("signals", {}).get("pa", {}).get("label", ""),
            "sarcasm":       result.get("signals", {}).get("sarcasm", {}).get("label", ""),
            "urgency":       result.get("signals", {}).get("urgency", {}).get("label", ""),
            "risk_count":    len(result.get("risk_flags", [])),
        })
        if (i+1) % 50 == 0: print(f"  Processed {i+1}/{len(emails)}")

    df_out = pd.DataFrame(records)
    df_out.to_csv(OUT_PATH, index=False)

    print(f"\n{'='*50}")
    print(f"RESULTS — {len(records)} emails evaluated")
    print(f"{'='*50}")
    print(f"Avg score:      {df_out['score'].mean():.1f}")
    print(f"Score dist:     {df_out['grade'].value_counts().to_dict()}")
    print(f"Tone dist:      {df_out['tone'].value_counts().to_dict()}")
    print(f"PA detected:    {(df_out['pa']=='passive_aggressive').sum()}")
    print(f"Sarcasm:        {(df_out['sarcasm']=='sarcastic').sum()}")
    print(f"Flagged emails: {(df_out['risk_count']>0).sum()}")
    print(f"\nSaved to {OUT_PATH}")

if __name__ == '__main__':
    main()
