"""
rewrite.py - Rewrite router with RAG status in response.
"""
from fastapi import APIRouter, HTTPException
from backend.schemas.schemas      import RewriteRequest
from backend.rewriter.groq_client import rewrite_email
from backend.rewriter.validator   import validate_intent_preservation

router = APIRouter(prefix="/api", tags=["rewrite"])

@router.post("/rewrite")
async def rewrite(req: RewriteRequest):
    if not req.email_text.strip():
        raise HTTPException(status_code=400, detail="Email text is required.")

    result = rewrite_email(
        original_email = req.email_text,
        analysis       = req.analysis,
        sender_name    = req.sender_name,
        receiver_name  = req.receiver_name,
    )

    if result["error"]:
        raise HTTPException(status_code=502, detail=f"Groq API error: {result['error']}")

    validation = validate_intent_preservation(req.email_text, result["rewritten_email"])

    return {
        "rewritten_email":  result["rewritten_email"],
        "subject_line":     result["subject_line"],
        "issues_fixed":     result["issues_fixed"],
        "rag_used":         result.get("rag_used", False),
        "similarity":       validation["similarity"],
        "intent_preserved": validation["preserved"],
        "warning":          validation["warning"],
    }