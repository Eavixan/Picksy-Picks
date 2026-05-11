# Backend API

FastAPI backend for the marketplace recommendation demo.

## Run

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- API health: http://127.0.0.1:8000/api/health
- API docs: http://127.0.0.1:8000/docs

## CORS setup

Default allowed frontend origins include local ports `5173`, `4173`, and `3000` on localhost/127.0.0.1.

For deployment, configure these optional env vars:

- `CORS_ORIGINS`: comma-separated explicit origins
- `CORS_ORIGIN_REGEX`: regex for dynamic origins (default supports `*.vercel.app`)

Example:

```bash
CORS_ORIGINS=https://your-frontend.vercel.app,http://127.0.0.1:4173
```

## Main endpoints

- `GET /api/bootstrap`
- `GET /api/recommendations?user_id=1560&model=Neural%20Matrix%20Factorization&top_k=10`
- `GET /api/users/1560/history`
- `GET /api/similar-users/1560`
- `GET /api/similar-items/405`
- `GET /api/sponsored?user_id=1560`
- `GET /api/clusters`

## Replace with latest notebook data

Run the export cell in `EXPORT_REAL_NOTEBOOK_DATA.md`, then copy the generated `demo-data.json` into:

```text
backend/data/demo-data.json
```

Restart the backend or call:

```bash
curl -X POST http://127.0.0.1:8000/api/reload
```
