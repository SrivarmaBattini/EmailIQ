"""
parser.py - Splits email thread into individual emails.
"""
import re

def split_thread(thread_text: str) -> list:
    """Split a pasted email thread into individual email bodies."""
    separators = [
        r'(?i)^On\s+.*?wrote:',
        r'(?i)-{5,}.*?Original Message.*?-{5,}',
        r'(?i)From:.*?Sent:.*?To:.*?Subject:',
        r'>{1,}\s*-{3,}',
    ]
    pattern = '|'.join(separators)
    parts   = re.split(pattern, thread_text, flags=re.MULTILINE)
    emails  = []
    for i, part in enumerate(reversed(parts)):
        cleaned = re.sub(r'^>.*$', '', part, flags=re.MULTILINE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) > 10:
            emails.append({"index": i + 1, "text": cleaned[:512]})
    return emails
