# Frontend Setup

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

Create `.env` in frontend folder:
```
VITE_API_URL=http://localhost:8000
```

## Deploy to Vercel (Free)

1. Push code to GitHub
2. Go to vercel.com → New Project
3. Import your GitHub repo
4. Set Root Directory to `frontend`
5. Add environment variable: `VITE_API_URL=https://your-render-backend-url.onrender.com`
6. Deploy

## Pages

| Route        | Description                        |
|--------------|------------------------------------|
| /            | Landing page                       |
| /analyse     | Single email analyser (main page)  |
| /thread      | Email thread tone drift analyser   |
| /dashboard   | Sender communication profile       |

## Tech Stack
- React 18 + Vite
- Tailwind CSS
- Recharts (charts)
- Lucide React (icons)
- React Hot Toast (notifications)
- Axios (API calls)
