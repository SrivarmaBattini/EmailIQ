# EmailIQ — Complete Setup Guide

## Project Structure
```
email-tone-optimizer/
├── data/raw/          ← Place your dataset files here
├── preprocessing/     ← Run these to prepare training data
├── training/          ← Colab notebook to train models
├── backend/           ← FastAPI backend
├── frontend/          ← React frontend
└── evaluation/        ← Test the pipeline
```

## Step 1 — Place Datasets

Copy files from your data zips into these folders:

```
data/raw/politeness/
  ├── politeness/politeness.tsv   (from data2.zip)
  ├── jigsaw/train.csv            (from data2.zip)
  └── stanford/test.csv           (from data2.zip)

data/raw/tone/
  ├── train.tsv                   (GoEmotions from data1.zip)
  ├── dev.tsv
  ├── test.tsv
  ├── emotions.txt
  └── ekman_mapping.json

data/raw/sarcasm/
  └── train-balanced-sarcasm.csv  (from data1.zip)

data/raw/enron/
  └── emails.csv                  (from data2.zip)

data/raw/combined/
  ├── final_dataset.csv           (from data1.zip)
  └── rewrite_dataset.csv         (from data1.zip)
```

## Step 2 — Run Preprocessing

```bash
pip install pandas scikit-learn
python preprocessing/run_all.py
```

This generates 14 CSV files in data/processed/

## Step 3 — Train Models (Google Colab)

1. Upload data/processed/ folder to Google Drive
2. Open training/train_all_models.ipynb in Colab
3. Set your HuggingFace username and token
4. Train each of the 7 models (change TASK index 0-6)
5. Models are automatically pushed to HuggingFace Hub

## Step 4 — Configure Environment

Edit `.env` in project root:
```
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
GROQ_MODEL=llama-3.1-8b-instant
HF_USER=your_hf_username
```

Get free Groq API key: https://console.groq.com
Get free HuggingFace token: https://huggingface.co/settings/tokens

## Step 5 — Run Backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## Step 6 — Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Step 7 — Deploy

Backend → Render.com (free): See backend/README.md
Frontend → Vercel (free): See frontend/README.md

## Notes

- Without trained models, base deberta-v3-small is used (reasonable results)
- Groq API is free at console.groq.com — no credit card needed
- Supabase is optional — sender profiles use in-memory storage if not configured
