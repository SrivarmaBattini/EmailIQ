"""
preprocessor.py - Cleans raw email text before passing to models.
"""
import re

ABBREVIATIONS = {
    "asap": "as soon as possible",
    "fyi":  "for your information",
    "eod":  "end of day",
    "eow":  "end of week",
    "pto":  "paid time off",
    "ooo":  "out of office",
    "lmk":  "let me know",
    "tbh":  "to be honest",
    "imo":  "in my opinion",
    "afaik":"as far as i know",
}

def expand_abbreviations(text: str) -> str:
    for abbr, full in ABBREVIATIONS.items():
        text = re.sub(rf'\b{abbr}\b', full, text, flags=re.IGNORECASE)
    return text

def strip_email_headers(text: str) -> str:
    text = re.sub(r'^(Message-ID|Date|From|To|Subject|Cc|Mime-Version|Content-Type'
                  r'|Content-Transfer-Encoding|X-\w+):.*$', '', text, flags=re.MULTILINE)
    return text

def strip_quoted_replies(text: str) -> str:
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'On .+wrote:', '', text, flags=re.DOTALL)
    text = re.sub(r'-{3,}.*', '', text, flags=re.DOTALL)
    return text

def strip_signature(text: str) -> str:
    lines = text.split('\n')
    clean = []
    for line in lines:
        if re.match(r'^(regards|best|thanks|cheers|sincerely|warm regards'
                    r'|kind regards|yours|sent from)', line.strip(), re.IGNORECASE):
            break
        clean.append(line)
    return '\n'.join(clean)

def clean_email(text: str, max_length: int = 512) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    text = strip_email_headers(text)
    text = strip_quoted_replies(text)
    text = strip_signature(text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = expand_abbreviations(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_length]
