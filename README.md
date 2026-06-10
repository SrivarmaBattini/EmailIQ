# EmailIQ — Professional Email Tone Optimizer

An advanced, locally-hosted LLM-powered professional email analysis and rewriting system. It detects tone, politeness, intent, passive-aggression, sarcasm, urgency, and power dynamics, then rewrites emails to be more professional using Groq API (Llama 3.1 8B) combined with RAG.

## Core Features
- **7 Parallel Custom DeBERTa-v3-small Models:** Trained specifically for email tone dimensions.
- **Hybrid Detection Engine:** Combines Ensemble Weighting of ML models and strict Rule Engines (specifically for Passive-Aggression and Sarcasm).
- **RAG-Powered Rewriting:** Automatically pulls top 3 examples from a local FAISS database of professional rewrites to guide the Llama 3.1 LLM.
- **Hierarchy-Aware:** Adapts rewrites based on power dynamics (Upward, Peer, Downward).
- **Thread-Level Analysis:** Detects tone drift over ongoing conversation threads.
- **Supabase Integration:** Handles user authentication and history tracking.

## Architecture & Stack
- **Backend:** FastAPI + Python (100% Local Execution)
- **Local Models:** 7x PyTorch DeBERTa models loaded directly into RAM
- **LLM API:** Groq API (Llama 3.1 8B) — Free & lightning fast
- **Frontend:** React + Tailwind CSS + Vite
- **Database:** Supabase (Auth & User History)

---

## Complete Local Setup Guide

### Step 1 — Configure Environment (.env)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=local
```
*(Get a free Groq API key at console.groq.com. Supabase is required for Dashboard/Login).*

### Step 2 — Run Backend (FastAPI)
Open a terminal and run the backend. This will automatically load your 7 custom PyTorch models directly into RAM from your `training/saved_models/` folder.
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```
*Note: Wait for the console to output `API ready` before clicking Analyse in the UI.*

### Step 3 — Run Frontend (React)
Open a second terminal for the frontend:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Datasets Used for Training
If you wish to view or retrain the models, these are the datasets used:
- **Enron Email Dataset:** ~1.36 GB (Extracted workplace communication structure)
- **Self-Annotated Reddit Corpus (SARC):** ~243 MB (Sarcasm detection)
- **GoEmotions:** ~25 MB (Tone mapping)
- **Stanford Politeness Corpus:** ~10 MB (Politeness scoring)
- **Jigsaw Toxic Comment:** ~80 MB (Passive-Aggression / Toxic intent)

These datasets were balanced and compiled into `final_dataset.csv` (80 MB) and `rewrite_dataset.csv` (27 MB) for model fine-tuning and RAG processing.
