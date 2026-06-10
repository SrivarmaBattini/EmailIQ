"""
main.py - FastAPI application entry point.
Loads all 7 DeBERTa models and initialises RAG at startup.
"""
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()


from backend.routers.analyse    import router as analyse_router
from backend.routers.rewrite    import router as rewrite_router
from backend.routers.thread     import router as thread_router
from backend.routers.sender     import router as sender_router
from backend.routers.chat       import router as chat_router

app = FastAPI(
    title       = "Email Tone Optimizer API",
    description = "NLP-powered professional email analysis and rewriting",
    version     = "1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins     = [FRONTEND_URL, "http://localhost:3000", "*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

@app.on_event("startup")
async def startup():
    print("API starting up. Models will be called via HuggingFace Inference API.")

    # Initialise RAG — safe even if CSV is missing
    try:
        from backend.rewriter.rag_retriever import setup_rag
        setup_rag()
    except Exception as e:
        print(f"  [RAG] Could not initialise (non-fatal): {e}")
        print("  [RAG] Rewriting will work without RAG examples.")

    print("API ready.")

@app.get("/")
def root():
    return {"status": "ok", "message": "Email Tone Optimizer API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/rag-status")
def rag_status():
    try:
        from backend.rewriter.rag_retriever import is_rag_available, get_collection
        col = get_collection()
        count = col.count() if col else 0
        return {
            "rag_available": is_rag_available(),
            "pairs_indexed": count,
        }
    except Exception:
        return {"rag_available": False, "pairs_indexed": 0}

app.include_router(analyse_router)
app.include_router(rewrite_router)
app.include_router(thread_router)
app.include_router(sender_router)
app.include_router(chat_router)