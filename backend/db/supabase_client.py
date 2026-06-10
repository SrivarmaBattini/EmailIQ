"""
supabase_client.py + sender_profiles.py combined.
Falls back to local JSON file storage if Supabase is not configured.
"""
import os, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase = None
LOCAL_STORE_FILE = "db/local_store.json"

def get_supabase():
    global _supabase
    if _supabase is None and SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client  # type: ignore
            _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Supabase init failed, using local JSON store: {e}")
    return _supabase

def _load_local_store():
    if os.path.exists(LOCAL_STORE_FILE):
        try:
            with open(LOCAL_STORE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def _save_local_store(data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(LOCAL_STORE_FILE), exist_ok=True)
    with open(LOCAL_STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def log_analysis(sender_name: str, email_text: str, score: int,
                 tone: str, risk_count: int, timestamp: str = None):
    ts = timestamp or datetime.utcnow().isoformat()
    record = {
        "sender_name": sender_name or "anonymous",
        "score":       score,
        "tone":        tone,
        "risk_count":  risk_count,
        "timestamp":   ts,
        "preview":     email_text[:100],
    }

    sb = get_supabase()
    if sb:
        try:
            sb.table("email_logs").insert(record).execute()
            return
        except Exception as e:
            print(f"Supabase insert failed: {e}")

    # Local JSON fallback
    key = sender_name or "anonymous"
    store = _load_local_store()
    if key not in store:
        store[key] = []
    store[key].append(record)
    _save_local_store(store)

def get_sender_profile(sender_name: str) -> dict:
    sb = get_supabase()
    records = []

    if sb:
        try:
            # Try exact match first
            resp = sb.table("email_logs") \
                     .select("*") \
                     .eq("sender_name", sender_name) \
                     .order("timestamp") \
                     .execute()
            records = resp.data or []
            
            if not records:
                search_name = sender_name.replace(" ", "")
                resp = sb.table("email_logs") \
                         .select("*") \
                         .eq("sender_name", search_name) \
                         .order("timestamp") \
                         .execute()
                records = resp.data or []
                
                # If still nothing, try capitalizing first letter
                if not records:
                    resp = sb.table("email_logs").select("*").eq("sender_name", search_name.capitalize()).order("timestamp").execute()
                    records = resp.data or []
        except Exception as e:
            print(f"Supabase fetch failed: {e}")

    if not records:
        store = _load_local_store()
        records = store.get(sender_name, [])

    if not records:
        return {
            "sender_name":       sender_name,
            "total_emails":      0,
            "average_score":     0,
            "score_history":     [],
            "tone_distribution": {},
            "flagged_count":     0,
        }

    scores   = [r["score"] for r in records]
    tones    = [r.get("tone", "unknown") for r in records]
    tone_dist = {}
    for t in tones:
        tone_dist[t] = tone_dist.get(t, 0) + 1

    history = [{"timestamp": r["timestamp"], "score": r["score"],
                "preview": r.get("preview", "")} for r in records[-30:]]

    return {
        "sender_name":       sender_name,
        "total_emails":      len(records),
        "average_score":     round(sum(scores) / len(scores), 1),
        "score_history":     history,
        "tone_distribution": tone_dist,
        "flagged_count":     sum(1 for r in records if r.get("risk_count", 0) > 0),
    }
