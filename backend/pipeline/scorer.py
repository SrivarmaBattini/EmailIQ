"""
scorer.py - Confidence-weighted professionalism score (0-100).
"""

BASE_SCORE = 70.0

MERITS = {
    "politeness": {"polite": 15},
    "tone":       {"professional": 15},
}

DEDUCTIONS = {
    "politeness":  {"impolite":          35},
    "tone":        {"aggressive":        35, "frustrated": 15},
    "pa":          {"passive_aggressive": 30},
    "sarcasm":     {"sarcastic":          25},
    "urgency":     {"high":              10},
}

GRADE_MAP = [
    (85, "Excellent",          "#22c55e"),
    (65, "Acceptable",         "#eab308"),
    (40, "Needs Improvement",  "#f97316"),
    (0,  "Poor",               "#ef4444"),
]

def compute_score(analysis: dict) -> dict:
    score = BASE_SCORE

    # Add Merit Points
    for task, bonuses in MERITS.items():
        result = analysis.get(task, {})
        label  = result.get("label", "")
        conf   = result.get("confidence", 0.0)
        if label in bonuses:
            bonus = bonuses[label] * conf
            score += bonus

    # Subtract Penalty Points
    for task, penalties in DEDUCTIONS.items():
        result = analysis.get(task, {})
        label  = result.get("label", "")
        conf   = result.get("confidence", 0.0)
        if label in penalties:
            deduction = penalties[label] * conf
            score -= deduction

    score = max(0.0, min(100.0, score))
    score_int = int(round(score))

    grade, color = "Poor", "#ef4444"
    for threshold, g, c in GRADE_MAP:
        if score_int >= threshold:
            grade, color = g, c
            break

    return {
        "score":  score_int,
        "grade":  grade,
        "color":  color,
    }
