# Email Tone Optimizer

An LLM-powered professional email analysis and rewriting system that detects tone, politeness, intent, passive-aggression, sarcasm, urgency, and power dynamics — then rewrites emails to be more professional using Groq API (Llama 3.1 8B).

## Features
- 7 parallel DeBERTa-v3-small classifiers
- Passive-aggression hybrid detection (model + rule engine)
- Hierarchy-aware rewriting (upward / peer / downward)
- Thread-level tone drift detection
- Sender profiling and history
- React frontend with real-time analysis

## Stack
- Backend: FastAPI + Python
- Models: DeBERTa-v3-small (HuggingFace)
- LLM: Groq API (Llama 3.1 8B) — Free
- Frontend: React + Tailwind CSS
- Deployment: Vercel (frontend) + Render.com (backend)

## Setup
See backend/README.md and frontend/README.md
