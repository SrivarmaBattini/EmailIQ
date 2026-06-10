from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
from backend.rewriter.groq_client import get_client

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

SYSTEM_PROMPT = """You are an expert Corporate Communications & Email Coach.
Your ONLY purpose is to help the user brainstorm, outline, and draft highly professional emails.
Do NOT answer general knowledge questions (like coding, math, history, etc.). If asked a non-email/non-work communication question, politely refuse and remind them you are an Email Coach.
Provide clear, actionable advice on tone, structure, and clarity.
If they ask you to write a draft, provide a professional, perfectly formatted email draft."""

@router.post("")
async def chat_with_coach(req: ChatRequest):
    client = get_client()
    if not client:
        raise HTTPException(status_code=500, detail="Groq client not initialized")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in req.messages:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=messages,
            max_tokens=800,
            temperature=0.6,
        )
        reply = resp.choices[0].message.content.strip()
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
