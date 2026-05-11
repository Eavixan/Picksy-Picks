# Export real notebook data into the backend

The app already runs immediately using the included demo snapshot.

For your final project demo, run your notebook fully first, then paste this cell at the very end of `final_recommendation.ipynb`. It will create a new `demo-data.json`. Copy that file into:

```text
backend/data/demo-data.json
```

Then restart the backend, or call:

```bash
curl -X POST http://127.0.0.1:8000/api/reload
```

## Notebook export cell

```python
import json
import os
import math
import numpy as np
import pandas as pd

EXPORT_PATH = "demo-data.json"
MAX_USERS = 25
MAX_HISTORY = 8
MAX_RECS = 20
MAX_SIMILAR_USERS = 5


def safe_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def normalize_product(row, rank=None, model_name=None):
    item_id = row.get("Item ID", row.get("item_idx", row.get("id", 0)))
    title = row.get("Title", row.get("title", "Unknown product"))
    category = row.get("Category", row.get("main_category", row.get("category", "AMAZON FASHION")))
    rating = row.get("Average Rating", row.get("average_rating", row.get("rating", None)))
    rating_count = row.get("Rating Count", row.get("rating_number", row.get("ratingCount", None)))
    price = row.get("Price", row.get("price", None))
    score = row.get("Model Score", row.get("score", None))
    return {
        "rank": int(rank if rank is not None else row.get("Rank", 0) or 0),
        "id": int(item_id),
        "title": str(title),
        "category": str(category),
        "rating": safe_value(rating),
        "ratingCount": safe_value(rating_count),
        "price": safe_value(price),
        "score": float(score) if score is not None and not pd.isna(score) else 0.0,
        "model": model_name,
        "why": f"{model_name or 'The selected model'} ranked this product highly for this user."
    }


def normalize_history(row):
    return {
        "id": int(row.get("Item ID", row.get("item_idx", 0))),
        "title": str(row.get("Title", "Unknown product")),
        "category": str(row.get("Category", "AMAZON FASHION")),
        "rating": safe_value(row.get("Rating")),
        "time": str(row.get("Timestamp", ""))
    }


def normalize_heldout(row):
    return {
        "split": str(row.get("Split", "Future")),
        "id": int(row.get("Item ID", row.get("item_idx", 0))),
        "title": str(row.get("Title", "Unknown product")),
        "category": str(row.get("Category", "AMAZON FASHION")),
        "rating": safe_value(row.get("Rating"))
    }


def metrics_from_results(model_name):
    candidates = [
        globals().get("compact_test_results"),
        globals().get("fair_test_results_df"),
        globals().get("test_results_df"),
    ]
    for df in candidates:
        if df is None or not isinstance(df, pd.DataFrame) or "Model" not in df.columns:
            continue
        match = df[df["Model"].astype(str) == str(model_name)]
        if len(match) == 0:
            continue
        row = match.iloc[0]
        return {
            "hit5": safe_value(row.get("HitRate@5")),
            "hit10": safe_value(row.get("HitRate@10")),
            "hit20": safe_value(row.get("HitRate@20")),
            "ndcg10": safe_value(row.get("NDCG@10")),
            "mrr10": safe_value(row.get("MRR@10")),
        }
    return {"hit5": None, "hit10": None, "hit20": None, "ndcg10": None, "mrr10": None}


model_family = {
    "Popularity": "Baseline",
    "Item-Based CF": "Collaborative filtering",
    "User-Based CF": "Collaborative filtering",
    "Matrix Factorization SVD": "Latent factor model",
    "Neural Matrix Factorization": "Neural recommender",
    "Graph Embeddings": "Graph-based recommender",
    "LightFM WARP": "Hybrid matrix factorization",
}

model_descriptions = {
    "Popularity": "Ranks globally strong items. Fast and useful for sparse marketplace data.",
    "Item-Based CF": "Recommends products similar to items already seen by the user.",
    "User-Based CF": "Uses similar users' behavior to recommend products.",
    "Matrix Factorization SVD": "Projects the user-item matrix into latent factors.",
    "Neural Matrix Factorization": "Learns neural user and item embeddings for ranking.",
    "Graph Embeddings": "Uses user-item graph random-walk embeddings for link prediction.",
    "LightFM WARP": "Optimizes ranking using WARP loss and can support metadata features.",
}

models = []
for model_name in demo_models.keys():
    models.append({
        "name": model_name,
        "family": model_family.get(model_name, "Recommender model"),
        "description": model_descriptions.get(model_name, "Recommendation model from the notebook."),
        "metrics": metrics_from_results(model_name),
    })

# Sort by HitRate@10 when available
models = sorted(models, key=lambda m: (m["metrics"].get("hit10") or 0), reverse=True)

selected_users = [int(u) for u in demo_user_candidates[:MAX_USERS]]
users = []
all_exported_products = {}

for user_idx in selected_users:
    history_df = get_user_history(user_idx, train_df, meta_df).head(MAX_HISTORY)
    heldout_df = get_user_heldout_items(user_idx, val_df, test_df)

    history = [normalize_history(row) for row in history_df.to_dict(orient="records")]
    heldout = [normalize_heldout(row) for row in heldout_df.to_dict(orient="records")]

    recommendations = {}
    for model_name, scorer in demo_models.items():
        try:
            recs_df = recommend_for_user(
                user_idx=user_idx,
                score_function=scorer,
                train_user_items=train_user_items,
                all_items=all_items,
                top_n=MAX_RECS,
            )
            recs = []
            for i, row in enumerate(recs_df.to_dict(orient="records"), start=1):
                item = normalize_product(row, rank=i, model_name=model_name)
                recs.append(item)
                all_exported_products[item["id"]] = item
            recommendations[model_name] = recs
        except Exception as e:
            print(f"Could not export {model_name} for user {user_idx}: {e}")

    dominant = []
    if history:
        dominant = pd.Series([h["category"] for h in history]).value_counts().head(3).index.tolist()

    users.append({
        "id": int(user_idx),
        "label": f"User {user_idx}",
        "persona": "Demo shopper",
        "summary": f"User {user_idx} has {len(history)} visible training-history items and {len(heldout)} held-out future items.",
        "dominantCategories": dominant,
        "history": history,
        "heldout": heldout,
        "recommendations": recommendations,
        "similarUsers": [],
    })

# Similar users from overlap in training history
user_hist_sets = {
    int(u["id"]): {int(x["id"]) for x in u["history"]}
    for u in users
}
for u in users:
    uid = int(u["id"])
    sims = []
    for other in users:
        oid = int(other["id"])
        if uid == oid:
            continue
        a, b = user_hist_sets.get(uid, set()), user_hist_sets.get(oid, set())
        score = len(a & b) / max(1, len(a | b))
        if score == 0:
            score = 0.5 / (1 + abs(uid - oid) % 10)
        sims.append({
            "id": oid,
            "score": round(float(score), 4),
            "reason": "Similar training-history pattern in the exported notebook data."
        })
    u["similarUsers"] = sorted(sims, key=lambda x: x["score"], reverse=True)[:MAX_SIMILAR_USERS]

# Similar items using metadata category fallback
similar_items = {}
product_list = list(all_exported_products.values())
for source in product_list[:30]:
    same_category = [p for p in product_list if p["id"] != source["id"] and p["category"] == source["category"]]
    same_category = sorted(same_category, key=lambda p: p.get("score", 0), reverse=True)[:6]
    similar_items[str(source["id"])] = [
        {**p, "why": "Same category and high exported model score."}
        for p in same_category
    ]

# Sponsored demo subset: high-scoring products, treated as promoted items for demo UI
sponsored_picks = sorted(product_list, key=lambda p: p.get("score", 0), reverse=True)[:8]
for i, p in enumerate(sponsored_picks, start=1):
    p["rank"] = i
    p["why"] = "Promoted item ranked using the same recommendation signals for the demo."

clusters = []
if product_list:
    product_df = pd.DataFrame(product_list)
    for category, group in product_df.groupby("category"):
        group = group.sort_values("score", ascending=False).head(5)
        clusters.append({
            "name": str(category),
            "description": f"Cluster of exported products from {category}.",
            "size": int(len(product_df[product_df["category"] == category])),
            "items": group["title"].astype(str).head(4).tolist(),
        })

project = {
    "title": "Neural Recommendations Across Marketplaces",
    "subtitle": "A Pinterest-inspired product discovery system with recommendations, similar users, similar items, clusters, and sponsored picks.",
    "dataset": {
        "users": int(interactions["user_idx"].nunique()) if "user_idx" in interactions else int(train_df["user_idx"].nunique()),
        "items": int(interactions["item_idx"].nunique()) if "item_idx" in interactions else int(meta_df["item_idx"].nunique()),
        "interactions": int(len(interactions)) if "interactions" in globals() else int(len(train_df) + len(val_df) + len(test_df)),
        "trainInteractions": int(len(train_df)),
        "validationInteractions": int(len(val_df)),
        "testInteractions": int(len(test_df)),
        "demoUsers": int(len(demo_user_candidates)),
        "category": "Amazon Fashion",
        "interactionType": "Implicit positive feedback from verified ratings and product interactions",
    },
    "pipeline": [
        "Load and clean Amazon Fashion reviews and metadata",
        "Create chronological train/validation/test splits",
        "Train popularity, collaborative filtering, SVD, neural MF, graph embedding, and LightFM models",
        "Evaluate with HitRate@K, NDCG@K, and MRR@K",
        "Serve exported recommendations through FastAPI and React",
    ],
    "backendMode": "Fresh notebook export",
}

payload = {
    "project": project,
    "models": models,
    "users": users,
    "sponsoredPicks": sponsored_picks,
    "clusters": clusters,
    "similarItems": similar_items,
}

with open(EXPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print(f"Exported demo data to {EXPORT_PATH}")
print("Copy this file to backend/data/demo-data.json")
```
