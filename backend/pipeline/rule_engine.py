"""
rule_engine.py - Hybrid PA detection: model + two-tier rule engine.
Tier 1: Exact phrase matching (confidence 0.85)
Tier 2: Regex soft signals (confidence 0.70)
Override: if rule_confidence > model_confidence → use rule result
"""
import re

TIER1_PHRASES = [
    "as per my last email", "as previously mentioned", "friendly reminder",
    "going forward", "as discussed", "per our conversation",
    "i imagine things must be very busy", "haven't heard back",
    "circling back", "just wanted to follow up again",
    "not sure if you saw my last message", "please advise",
    "i'll leave this with you", "as i mentioned before",
    "i trust this is clear", "as clearly stated",
    "i am surprised that", "i would have expected",
    "not sure how else to explain", "maybe i wasn't clear",
    "with all due respect", "no offence but",
    "i guess i'll just", "i suppose i have to",
    "noted.", "good to know.", "understood.",
    "as you can see", "obviously", "clearly you",
    "i shouldn't have to", "you were supposed to",
    "as expected", "challenging for some people",
    "missed again", "review your responsibilities",
]

TIER2_PATTERNS = [
    r'\bjust\s+\w+ing\b',           # "just checking", "just following up"
    r'\bwhen\s+you\s+get\s+a\s+chance\b',
    r'\bno\s+worries\b.*\bbut\b',   # "no worries but..."
    r'\bhope\s+this\s+helps\b',
    r'\bdo\s+the\s+needful\b',
    r'\bkindly\s+revert\b',
    r'\bas\s+per\b',
    r'\bfor\s+your\s+reference\b.*\bagain\b',
    r'\bi\s+mentioned\s+this\s+before\b',
    r'\bplease\s+read\s+carefully\b',
]

def rule_engine_score(text: str) -> dict:
    text_lower = text.lower().strip()

    # Tier 1 - exact phrase
    for phrase in TIER1_PHRASES:
        if phrase in text_lower:
            return {"pa": True, "confidence": 1.0, "source": "rule_tier1", "phrase": phrase}

    # Tier 2 - regex soft signals (accumulate)
    matches = []
    for pattern in TIER2_PATTERNS:
        if re.search(pattern, text_lower):
            matches.append(pattern)

    if len(matches) >= 2:
        return {"pa": True, "confidence": 0.75, "source": "rule_tier2", "matches": matches}
    elif len(matches) == 1:
        return {"pa": False, "confidence": 0.55, "source": "rule_tier2_weak", "matches": matches}

    return {"pa": False, "confidence": 0.0, "source": "no_rule_match"}

SAFE_PHRASES = [
    "follow up on",
    "wanted to check in",
    "any updates or next steps",
    "check in and see",
]

def hybrid_pa_result(model_result: dict, text: str) -> dict:
    """
    Combines model output with rule engine using Ensemble Weighting.
    Final Confidence = (Model Confidence * 0.6) + (Rule Confidence * 0.4)
    """
    rule = rule_engine_score(text)
    
    # If the model didn't classify it as PA, the confidence for PA is essentially 1 - confidence
    # But since the model output is just the max confidence of whatever label it chose:
    # We should get the actual PA probability. Luckily, `model_result["scores"]` has the raw probabilities.
    raw_scores = model_result.get("scores", {})
    model_pa_prob = raw_scores.get("passive_aggressive", 0.0)

    rule_conf = rule["confidence"]
    
    text_lower = text.lower().strip()
    
    # 1. White-list Override (Extreme Safety)
    # If it contains very polite safe phrases, we still want to strongly reduce PA probability
    for safe in SAFE_PHRASES:
        if safe in text_lower:
            # Force low PA probability
            rule_conf = 0.0
            model_pa_prob *= 0.2 # Dramatically reduce model's PA score

    # 2. Ensemble Weighting Math
    final_pa_confidence = (model_pa_prob * 0.6) + (rule_conf * 0.4)
    
    # Threshold for deciding it's PA
    if final_pa_confidence >= 0.5:
        return {
            "label":      "passive_aggressive",
            "confidence": round(final_pa_confidence, 4),
            "scores":     raw_scores,
            "source":     "ensemble_blended",
            "triggered":  rule.get("phrase") or rule.get("matches", []),
        }
    else:
        # If it's neutral, we invert the confidence to represent "neutral confidence"
        return {
            "label":      "neutral",
            "confidence": round(1.0 - final_pa_confidence, 4),
            "scores":     raw_scores,
            "source":     "ensemble_blended",
            "triggered":  [],
        }

SARCASM_PATTERNS = [
    r'\boh,\s+great\b',
    r'\bwhat\s+a\s+surprise\b',
    r'\bso\s+helpful\b',
    r'\bthanks\s+for\s+nothing\b',
    r'\bfascinating\b',
    r'\byeah,\s+right\b',
    r'\bsure,\s+that\s+makes\s+sense\b',
    r'\bas\s+if\b',
    r'\bbig\s+help\b',
    r'\bwow,\s+thanks\b',
]

def rule_engine_sarcasm_score(text: str) -> dict:
    text_lower = text.lower().strip()
    matches = []
    for pattern in SARCASM_PATTERNS:
        if re.search(pattern, text_lower):
            matches.append(pattern)

    if len(matches) >= 1:
        return {"sarcastic": True, "confidence": 1.0, "source": "rule_tier1", "matches": matches}
    
    return {"sarcastic": False, "confidence": 0.0, "source": "no_rule_match"}

def hybrid_sarcasm_result(model_result: dict, text: str) -> dict:
    """
    Combines model output with rule engine for sarcasm using Ensemble Weighting.
    """
    rule = rule_engine_sarcasm_score(text)
    
    raw_scores = model_result.get("scores", {})
    model_sarcasm_prob = raw_scores.get("sarcastic", 0.0)
    rule_conf = rule["confidence"]

    # Ensemble Weighting
    final_sarcasm_confidence = (model_sarcasm_prob * 0.6) + (rule_conf * 0.4)

    if final_sarcasm_confidence >= 0.5:
        return {
            "label":      "sarcastic",
            "confidence": round(final_sarcasm_confidence, 4),
            "scores":     raw_scores,
            "source":     "ensemble_blended",
            "triggered":  rule.get("matches", []),
        }
    else:
        return {
            "label":      "neutral",
            "confidence": round(1.0 - final_sarcasm_confidence, 4),
            "scores":     raw_scores,
            "source":     "ensemble_blended",
            "triggered":  [],
        }
