from fastapi import APIRouter, HTTPException
from backend.schemas.schemas import AnalyseRequest, AnalyseResponse
from backend.pipeline.preprocessor import clean_email
from backend.pipeline.analyser     import analyse_email
from backend.pipeline.rule_engine  import hybrid_pa_result, hybrid_sarcasm_result
from backend.pipeline.scorer       import compute_score
from backend.pipeline.risk_flags   import evaluate_risk_flags
from backend.db.supabase_client    import log_analysis

router = APIRouter(prefix="/api", tags=["analyse"])

@router.post("/analyse")
async def analyse(req: AnalyseRequest):
    if not req.email_text.strip():
        raise HTTPException(status_code=400, detail="Email text is required.")

    cleaned   = clean_email(req.email_text)
    analysis  = analyse_email(cleaned)

    # Override power dynamic if user selected relationship
    if req.relationship and req.relationship in ["upward","peer","downward"]:
        analysis["power"] = {
            "label":      req.relationship,
            "confidence": 1.0,
            "scores":     {req.relationship: 1.0},
            "source":     "user_selected",
        }

    # Apply hybrid PA detection
    analysis["pa"] = hybrid_pa_result(analysis.get("pa", {}), cleaned)

    score      = compute_score(analysis)
    risk_flags = evaluate_risk_flags(analysis)

    # Log to Supabase / memory
    if req.sender_name:
        log_analysis(
            sender_name = req.sender_name,
            email_text  = req.email_text,
            score       = score["score"],
            tone        = analysis.get("tone", {}).get("label", "unknown"),
            risk_count  = len(risk_flags),
        )

    return {
        "cleaned_text": cleaned,
        "signals":      analysis,
        "score":        score,
        "risk_flags":   risk_flags,
    }
