# Backend Setup

## Local Development

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
HF_USER=your_huggingface_username
SUPABASE_URL=your_supabase_url        # optional
SUPABASE_KEY=your_supabase_anon_key   # optional
FRONTEND_URL=http://localhost:5173
```

Run the server:
```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Deploy to Render.com (Free)

1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set Build Command: `pip install -r backend/requirements.txt`
5. Set Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard
7. Deploy

## Endpoints

| Method | URL                    | Description             |
|--------|------------------------|-------------------------|
| POST   | /api/analyse           | Analyse single email    |
| POST   | /api/rewrite           | Rewrite email with Groq |
| POST   | /api/analyse-thread    | Analyse email thread    |
| GET    | /api/sender/{name}     | Get sender profile      |
| GET    | /health                | Health check            |

## Model Training

After preprocessing, upload processed CSVs to Google Drive.
Open `training/train_all_models.ipynb` in Google Colab (free T4 GPU).
Train each model and push to HuggingFace Hub.
Set `HF_USER` in your `.env` to load your trained models.

Without trained models, the system uses the base `microsoft/deberta-v3-small`
which will give reasonable but not domain-specific results.
