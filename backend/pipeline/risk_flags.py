"""
risk_flags.py - 6 cross-signal risk rules for workplace communication.
"""

RISK_RULES = [
    {
        "id":      "hostile_workplace",
        "level":   "HIGH",
        "color":   "#ef4444",
        "title":   "Hostile Workplace Communication",
        "message": "Aggressive tone detected in a downward communication. This may constitute hostile workplace behavior.",
        "condition": lambda a: (a.get("tone", {}).get("label") == "aggressive"
                                and a.get("power", {}).get("label") == "downward"),
    },
    {
        "id":      "burnout_signal",
        "level":   "MEDIUM",
        "color":   "#f97316",
        "title":   "Burnout Signal",
        "message": "Frustrated tone combined with high urgency may indicate the sender is under significant stress.",
        "condition": lambda a: (a.get("tone", {}).get("label") == "frustrated"
                                and a.get("urgency", {}).get("label") == "high"),
    },
    {
        "id":      "covert_pa",
        "level":   "MEDIUM",
        "color":   "#f97316",
        "title":   "Covert Passive-Aggression",
        "message": "Surface-level politeness is masking passive-aggressive intent. This is harder to detect but damages relationships.",
        "condition": lambda a: (a.get("pa", {}).get("label") == "passive_aggressive"
                                and a.get("politeness", {}).get("label") == "polite"),
    },
    {
        "id":      "condescending",
        "level":   "HIGH",
        "color":   "#ef4444",
        "title":   "Condescending Communication",
        "message": "Sarcasm detected in a downward communication. This can severely damage team morale and trust.",
        "condition": lambda a: (a.get("sarcasm", {}).get("label") == "sarcastic"
                                and a.get("power", {}).get("label") == "downward"),
    },
    {
        "id":      "career_risk",
        "level":   "HIGH",
        "color":   "#ef4444",
        "title":   "Career Risk",
        "message": "Passive-aggressive language detected in an upward communication. This could seriously harm your professional reputation.",
        "condition": lambda a: (a.get("pa", {}).get("label") == "passive_aggressive"
                                and a.get("power", {}).get("label") == "upward"),
    },
    {
        "id":      "escalation_risk",
        "level":   "MEDIUM",
        "color":   "#f97316",
        "title":   "Escalation Risk",
        "message": "Combination of impolite tone and passive-aggression may escalate the situation.",
        "condition": lambda a: (a.get("pa", {}).get("label") == "passive_aggressive"
                                and a.get("politeness", {}).get("label") == "impolite"),
    },
]

def evaluate_risk_flags(analysis: dict) -> list:
    triggered = []
    for rule in RISK_RULES:
        try:
            if rule["condition"](analysis):
                triggered.append({
                    "id":      rule["id"],
                    "level":   rule["level"],
                    "color":   rule["color"],
                    "title":   rule["title"],
                    "message": rule["message"],
                })
        except Exception:
            pass
    return triggered
