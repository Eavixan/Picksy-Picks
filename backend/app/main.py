from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .recommender_service import RecommenderService

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "demo-data.json"

service = RecommenderService(DATA_PATH)

app = FastAPI(
    title="Marketplace Recommender API",
    description="FastAPI backend for the CSE427 recommendation system demo.",
    version="1.0.0",
)


def _parse_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw.strip():
        return default_origins
    parsed = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return parsed or default_origins


cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Marketplace Recommender API is running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return service.health()


@app.post("/api/reload")
def reload_data():
    service.reload()
    return {"message": "Data reloaded", "health": service.health()}


@app.get("/api/bootstrap")
def bootstrap():
    return service.bootstrap()


@app.get("/api/models")
def models():
    return {"models": service.list_models()}


@app.get("/api/users")
def users():
    return {"users": service.list_users()}


@app.get("/api/users/{user_id}")
def user_detail(user_id: int):
    try:
        return service.get_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/users/{user_id}/history")
def user_history(user_id: int):
    try:
        return service.get_history(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/recommendations")
def recommendations(
    user_id: int = Query(..., description="Demo user index"),
    model: Optional[str] = Query(None, description="Model name"),
    top_k: int = Query(10, ge=1, le=50, description="Number of recommendations"),
):
    try:
        return service.recommend(user_id=user_id, model=model, top_k=top_k)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/similar-users/{user_id}")
def similar_users(user_id: int, top_k: int = Query(5, ge=1, le=20)):
    try:
        return service.similar_users(user_id=user_id, top_k=top_k)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/similar-items/{item_id}")
def similar_items(item_id: str, top_k: int = Query(6, ge=1, le=20)):
    return service.similar_items(item_id=item_id, top_k=top_k)


@app.get("/api/sponsored")
def sponsored(user_id: Optional[int] = None, top_k: int = Query(5, ge=1, le=20)):
    return service.sponsored(user_id=user_id, top_k=top_k)


@app.get("/api/clusters")
def clusters():
    return {"clusters": service.get_clusters()}


@app.get("/api/search")
def search(q: str = "", limit: int = Query(20, ge=1, le=100)):
    return service.search_products(q=q, limit=limit)
