"""
drift_detector.py - Detects tone drift across an email thread.
"""

def detect_drift(thread_scores: list) -> dict:
    """
    thread_scores: list of int scores per email (oldest first)
    Returns drift direction and summary.
    """
    if len(thread_scores) < 2:
        return {"direction": "stable", "summary": "Not enough emails to detect drift."}

    first_half = thread_scores[:len(thread_scores)//2]
    second_half= thread_scores[len(thread_scores)//2:]

    avg_first  = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    diff       = avg_second - avg_first

    if diff <= -10:
        direction = "deteriorating"
        summary   = f"The conversation tone has worsened by {abs(diff):.0f} points. Intervention recommended."
    elif diff >= 10:
        direction = "improving"
        summary   = f"The conversation tone has improved by {diff:.0f} points."
    else:
        direction = "stable"
        summary   = "The conversation tone is relatively stable."

    # Find worst email
    worst_idx   = int(thread_scores.index(min(thread_scores)))
    worst_score = min(thread_scores)

    return {
        "direction":    direction,
        "summary":      summary,
        "avg_start":    round(avg_first, 1),
        "avg_end":      round(avg_second, 1),
        "worst_index":  worst_idx + 1,
        "worst_score":  worst_score,
        "scores":       thread_scores,
    }
