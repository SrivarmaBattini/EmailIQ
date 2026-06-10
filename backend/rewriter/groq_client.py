"""
groq_client.py - Groq API with RAG-enhanced prompting.
RAG fetches similar email examples before rewriting.
Falls back gracefully if RAG is unavailable.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def rewrite_email(
    original_email: str,
    analysis: dict,
    sender_name: str = "",
    receiver_name: str = "",
) -> dict:

    tone       = analysis.get("tone",       {}).get("label", "unknown")
    politeness = analysis.get("politeness", {}).get("label", "unknown")
    intent     = analysis.get("intent",     {}).get("label", "unknown")
    pa         = analysis.get("pa",         {}).get("label", "neutral")
    sarcasm    = analysis.get("sarcasm",    {}).get("label", "neutral")
    urgency    = analysis.get("urgency",    {}).get("label", "low")
    power      = analysis.get("power",      {}).get("label", "peer")

    issues = []
    if tone in ["aggressive", "frustrated"]:
        issues.append(f"{tone} tone")
    if politeness == "impolite":
        issues.append("impolite language")
    if pa == "passive_aggressive":
        issues.append("passive-aggressive phrasing")
    if sarcasm == "sarcastic":
        issues.append("sarcastic language")
    issues_str = ", ".join(issues) if issues else "minor tone improvements needed"

    power_instruction = {
        "upward":   "Writing to someone senior. Use respectful, deferential language.",
        "peer":     "Writing to a colleague. Use collaborative, professional language.",
        "downward": "Writing to someone junior. Use clear, respectful language.",
    }.get(power, "Use professional language.")

    urgency_instruction = {
        "high":   "Urgent matter. Keep concise and action-oriented while professional.",
        "medium": "Moderate priority. Balance professionalism with clarity.",
        "low":    "No time pressure. Focus on warmth and thoroughness.",
    }.get(urgency, "")

    # Try RAG retrieval — silent fallback if unavailable
    rag_section = ""
    rag_used    = False
    try:
        from backend.rewriter.rag_retriever import retrieve_similar_examples, is_rag_available
        if is_rag_available():
            examples = retrieve_similar_examples(original_email, n=3)
            if examples:
                lines = []
                for i, ex in enumerate(examples, 1):
                    lines.append(
                        f"Example {i}:\n"
                        f"  Original:  {ex['original']}\n"
                        f"  Rewritten: {ex['rewritten']}"
                    )
                rag_section = (
                    "\nHere are similar emails that were rewritten professionally. "
                    "Use them as style reference only — do not copy directly:\n\n"
                    + "\n\n".join(lines)
                    + "\n"
                )
                rag_used = True
    except Exception:
        rag_section = ""
        rag_used    = False

    prompt = f"""You are a professional workplace communication expert.

TASK: Rewrite the email below to fix all detected issues while preserving the original intent exactly.

DETECTED ISSUES: {issues_str}
ORIGINAL INTENT: {intent}
POWER DYNAMIC: {power_instruction}
URGENCY: {urgency_instruction}
{rag_section}
STRICT RULES:
1. Fix every detected issue
2. Keep the original meaning and intent — do not add or remove information
3. Keep similar length to the original
4. Do not add greetings or sign-offs unless already in the original
5. Return ONLY the rewritten email. No explanations.

ORIGINAL EMAIL:
{original_email}

REWRITTEN EMAIL:"""

    subject_prompt = f"""Write a concise professional subject line for this email.
Under 10 words. Return ONLY the subject line, nothing else.
Intent: {intent}

EMAIL:
{original_email}"""

    try:
        rewrite_resp = get_client().chat.completions.create(
            model       = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 600,
            temperature = 0.3,
        )
        rewritten = rewrite_resp.choices[0].message.content.strip()

        subject_resp = get_client().chat.completions.create(
            model       = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages    = [{"role": "user", "content": subject_prompt}],
            max_tokens  = 30,
            temperature = 0.2,
        )
        subject_line = subject_resp.choices[0].message.content.strip()

        return {
            "rewritten_email": rewritten,
            "subject_line":    subject_line,
            "issues_fixed":    issues,
            "rag_used":        rag_used,
            "error":           None,
        }

    except Exception as e:
        return {
            "rewritten_email": original_email,
            "subject_line":    "",
            "issues_fixed":    [],
            "rag_used":        False,
            "error":           str(e),
        }