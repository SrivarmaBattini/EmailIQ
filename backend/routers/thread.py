from fastapi import APIRouter, HTTPException
from backend.schemas.schemas          import ThreadRequest
from backend.thread.parser            import split_thread
from backend.thread.drift_detector    import detect_drift
from backend.pipeline.preprocessor    import clean_email
from backend.pipeline.analyser        import analyse_email
from backend.pipeline.rule_engine     import hybrid_pa_result, hybrid_sarcasm_result
from backend.pipeline.scorer          import compute_score

router = APIRouter(prefix="/api", tags=["thread"])

@router.post("/analyse-thread")
async def analyse_thread(req: ThreadRequest):
    if not req.thread_text.strip():
        raise HTTPException(status_code=400, detail="Thread text is required.")

    emails  = split_thread(req.thread_text)
    if not emails:
        raise HTTPException(status_code=400, detail="Could not parse any emails from thread.")

    results = []
    scores  = []

    for email_item in emails:
        cleaned  = clean_email(email_item["text"])
        analysis = analyse_email(cleaned)
        analysis["pa"] = hybrid_pa_result(analysis.get("pa", {}), cleaned)
        analysis["sarcasm"] = hybrid_sarcasm_result(analysis.get("sarcasm", {}), cleaned)
        score    = compute_score(analysis)

        scores.append(score["score"])
        results.append({
            "index": email_item["index"],
            "text":  email_item["text"],
            "score": score["score"],
            "grade": score["grade"],
            "color": score["color"],
            "signals": {
                "tone":       analysis.get("tone",  {}).get("label"),
                "politeness": analysis.get("politeness", {}).get("label"),
                "pa":         analysis.get("pa",    {}).get("label"),
            }
        })

    drift = detect_drift(scores)

    return {"emails": results, "drift": drift}
