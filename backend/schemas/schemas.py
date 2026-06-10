"""
request_schemas.py and response_schemas.py combined.
"""
from pydantic import BaseModel
from typing   import Optional, List, Dict, Any

# ── Request schemas ──────────────────────────────────────
class AnalyseRequest(BaseModel):
    email_text:    str
    sender_name:   Optional[str] = ""
    receiver_name: Optional[str] = ""
    relationship:  Optional[str] = "peer"  # upward | peer | downward

class RewriteRequest(BaseModel):
    email_text:    str
    analysis:      Dict[str, Any]
    sender_name:   Optional[str] = ""
    receiver_name: Optional[str] = ""

class ThreadRequest(BaseModel):
    thread_text:   str
    sender_name:   Optional[str] = ""

# ── Response schemas ─────────────────────────────────────
class SignalResult(BaseModel):
    label:      str
    confidence: float
    scores:     Dict[str, float]

class ScoreResult(BaseModel):
    score: int
    grade: str
    color: str

class RiskFlag(BaseModel):
    id:      str
    level:   str
    color:   str
    title:   str
    message: str

class AnalyseResponse(BaseModel):
    cleaned_text: str
    signals:      Dict[str, Any]
    score:        ScoreResult
    risk_flags:   List[RiskFlag]

class RewriteResponse(BaseModel):
    rewritten_email:  str
    subject_line:     str
    issues_fixed:     List[str]
    similarity:       float
    intent_preserved: bool
    warning:          Optional[str]

class ThreadEmailResult(BaseModel):
    index: int
    text:  str
    score: int
    grade: str

class ThreadResponse(BaseModel):
    emails:    List[ThreadEmailResult]
    drift:     Dict[str, Any]

class SenderProfile(BaseModel):
    sender_name:       str
    total_emails:      int
    average_score:     float
    score_history:     List[Dict[str, Any]]
    tone_distribution: Dict[str, int]
    flagged_count:     int
