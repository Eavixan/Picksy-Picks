from __future__ import annotations

import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional


class RecommenderService:
    """Small API service layer around exported notebook recommendation data.

    The uploaded notebook trains/evaluates models inside Jupyter. A notebook file does not
    keep live Python model objects in a form FastAPI can import. So this backend serves the
    notebook's exported recommendation snapshot. Replace backend/data/demo-data.json with a
    fresh export from the notebook to make the API show your latest real model outputs.
    """

    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)
        self.data: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        self.data = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.models_by_name = {m["name"]: m for m in self.data.get("models", [])}
        self.product_pool = self._collect_products()
        self.demo_users = self._build_demo_users()
        self.users_by_id = {int(u["id"]): u for u in self.demo_users}

    def _collect_products(self) -> List[Dict[str, Any]]:
        products: Dict[int, Dict[str, Any]] = {}
        for user in self.data.get("users", []):
            for row in user.get("history", []):
                products[str(row["id"])] = self._normalise_product(row)
            for row in user.get("heldout", []):
                products[str(row["id"])] = self._normalise_product(row)
            for items in user.get("recommendations", {}).values():
                for row in items:
                    products[str(row["id"])] = self._normalise_product(row)
        for row in self.data.get("sponsoredPicks", []):
            products[str(row["id"])] = self._normalise_product(row)
        for items in self.data.get("similarItems", {}).values():
            for row in items:
                products[str(row["id"])] = self._normalise_product(row)
        return list(products.values())

    def _clean_id(self, value: Any) -> Any:
        try:
            if isinstance(value, str) and not value.isdigit():
                return value
            return int(value)
        except Exception:
            return str(value)

    def _id_number(self, value: Any) -> int:
        try:
            return int(value)
        except Exception:
            return sum(ord(ch) for ch in str(value))

    def _normalise_product(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": self._clean_id(row.get("id") or row.get("Item ID") or row.get("item_id") or 0),
            "title": str(row.get("title") or row.get("Title") or "Unknown product"),
            "category": str(row.get("category") or row.get("Category") or "AMAZON FASHION"),
            "rating": row.get("rating") if row.get("rating") is not None else row.get("Average Rating"),
            "ratingCount": row.get("ratingCount") if row.get("ratingCount") is not None else row.get("Rating Count"),
            "price": row.get("price") if row.get("price") is not None else row.get("Price"),
            "score": float(row.get("score") or row.get("Model Score") or 0.0),
            "why": row.get("why", "Relevant product from the recommendation dataset."),
        }

    def _build_demo_users(self) -> List[Dict[str, Any]]:
        users = deepcopy(self.data.get("users", []))
        existing_ids = {int(u["id"]) for u in users}
        personas = [
            ("User 450", 450, "Silver accessory loyalist", ["silver", "bracelet", "necklace"], ["AMAZON FASHION", "Silver", "Accessories"]),
            ("User 360", 360, "Statement jewelry browser", ["statement", "necklace", "bead"], ["AMAZON FASHION", "Statement Jewelry", "Necklaces"]),
            ("User 324", 324, "Gift jewelry shopper", ["gift", "heart", "charm"], ["AMAZON FASHION", "Gifts", "Charm Jewelry"]),
            ("User 10001", 10001, "Minimal bracelet fan", ["bracelet", "bangle", "silver"], ["AMAZON FASHION", "Bracelets", "Minimal Style"]),
            ("User 10002", 10002, "Colorful bead explorer", ["bead", "purple", "enamel"], ["AMAZON FASHION", "Beaded Jewelry", "Color"]),
            ("User 10003", 10003, "Classic necklace seeker", ["necklace", "chain", "pendant"], ["AMAZON FASHION", "Necklaces", "Classic"]),
            ("User 10004", 10004, "Ring and gemstone shopper", ["ring", "gem", "zirconia"], ["AMAZON FASHION", "Rings", "Gemstones"]),
            ("User 10005", 10005, "Fashion watch comparer", ["watch", "strap", "band"], ["AMAZON FASHION", "Watches", "Accessories"]),
            ("User 10006", 10006, "Pearl style shopper", ["pearl", "white", "elegant"], ["AMAZON FASHION", "Pearls", "Elegant"]),
            ("User 10007", 10007, "Boho accessory buyer", ["tribal", "leaf", "vintage"], ["AMAZON FASHION", "Boho", "Statement Jewelry"]),
            ("User 10008", 10008, "Budget deal hunter", ["sale", "price", "value"], ["AMAZON FASHION", "Value Picks", "Popular"]),
            ("User 10009", 10009, "Premium gift curator", ["luxury", "gift", "sterling"], ["AMAZON FASHION", "Premium", "Gifts"]),
            ("User 10010", 10010, "Everyday earrings shopper", ["earring", "stud", "drop"], ["AMAZON FASHION", "Earrings", "Everyday"]),
            ("User 10011", 10011, "Charm bracelet builder", ["charm", "bracelet", "sterling"], ["AMAZON FASHION", "Charm Jewelry", "Bracelets"]),
            ("User 10012", 10012, "Occasion accessory planner", ["wedding", "party", "crystal"], ["AMAZON FASHION", "Occasion", "Accessories"]),
            ("User 10013", 10013, "Casual fashion browser", ["fashion", "casual", "style"], ["AMAZON FASHION", "Casual", "Discovery"]),
            ("User 10014", 10014, "Highly rated item picker", ["rating", "popular", "review"], ["AMAZON FASHION", "Top Rated", "Popular"]),
            ("User 10015", 10015, "Personalized discovery tester", ["recommend", "similar", "match"], ["AMAZON FASHION", "Discovery", "Personalized"]),
        ]

        for label, user_id, persona, keywords, categories in personas:
            if user_id in existing_ids:
                continue
            history = self._pick_products_for_keywords(keywords, offset=user_id, limit=6)
            heldout = self._pick_products_for_keywords(keywords, offset=user_id + 7, limit=2)
            users.append({
                "id": user_id,
                "label": label,
                "persona": persona,
                "summary": f"Generated demo profile emphasizing {', '.join(categories[1:]).lower()} within the exported marketplace catalog.",
                "dominantCategories": categories,
                "history": history,
                "heldout": [
                    {**item, "split": "Validation" if idx == 0 else "Test"}
                    for idx, item in enumerate(heldout)
                ],
                "similarUsers": [],
                "recommendations": {},
            })
        return users

    def _pick_products_for_keywords(self, keywords: List[str], offset: int, limit: int) -> List[Dict[str, Any]]:
        scored = []
        for product in self.product_pool:
            text = f"{product.get('title', '')} {product.get('category', '')} {product.get('why', '')}".lower()
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches:
                scored.append((matches, self._id_number(product["id"]), product))
        if not scored:
            scored = [(0, self._id_number(product["id"]), product) for product in self.product_pool]
        scored.sort(key=lambda row: (-row[0], (row[1] + offset) % 997))
        picked = []
        seen = set()
        for _, _, product in scored:
            if str(product["id"]) in seen:
                continue
            item = deepcopy(product)
            item["rating"] = item.get("rating") or 5
            item["score"] = item.get("score") or 0.5
            picked.append(item)
            seen.add(str(product["id"]))
            if len(picked) >= limit:
                break
        return picked

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "mode": "local-demo-api",
            "dataFile": str(self.data_path),
            "users": len(self.users_by_id),
            "models": len(self.models_by_name),
            "products": len(self.product_pool),
        }

    def bootstrap(self) -> Dict[str, Any]:
        return {
            "project": self.data.get("project", {}),
            "models": self.list_models(),
            "users": self.list_users(),
            "clusters": self.get_clusters(),
            "health": self.health(),
        }

    def list_models(self) -> List[Dict[str, Any]]:
        return deepcopy(self.data.get("models", []))

    def list_users(self) -> List[Dict[str, Any]]:
        users = []
        for u in self.demo_users:
            users.append({
                "id": int(u["id"]),
                "label": u.get("label", f"User {u['id']}"),
                "persona": u.get("persona", "Demo shopper"),
                "summary": u.get("summary", "Demo user from the recommendation dataset."),
                "dominantCategories": u.get("dominantCategories", []),
                "historyCount": len(u.get("history", [])),
                "availableModels": list(u.get("recommendations", {}).keys()),
            })
        return users

    def get_user(self, user_id: int) -> Dict[str, Any]:
        user = self.users_by_id.get(int(user_id))
        if not user:
            raise KeyError(f"User {user_id} was not found in demo-data.json")
        return deepcopy(user)

    def get_history(self, user_id: int) -> Dict[str, Any]:
        user = self.get_user(user_id)
        return {
            "userId": int(user_id),
            "history": user.get("history", []),
            "heldout": user.get("heldout", []),
        }

    def recommend(self, user_id: int, model: Optional[str] = None, top_k: int = 10) -> Dict[str, Any]:
        user = self.get_user(user_id)
        recs_by_model = user.get("recommendations", {})
        model_name = model or self._default_model_for_user(user)

        if model_name in recs_by_model:
            recs = deepcopy(recs_by_model[model_name])
        else:
            recs = self._fallback_recommendations(user, model_name)

        recs = self._rank_and_limit(recs, top_k, model_name)
        return {
            "userId": int(user_id),
            "model": model_name,
            "topK": int(top_k),
            "count": len(recs),
            "recommendations": recs,
        }

    def _default_model_for_user(self, user: Dict[str, Any]) -> str:
        options = list(user.get("recommendations", {}).keys())
        if "Neural Matrix Factorization" in options:
            return "Neural Matrix Factorization"
        if options:
            return options[0]
        return next(iter(self.models_by_name.keys()), "Popularity")

    def _fallback_recommendations(self, user: Dict[str, Any], model_name: str) -> List[Dict[str, Any]]:
        """Create deterministic fallback recommendations for models without exported rows.

        This keeps every model dropdown functional during localhost testing. For final demo
        accuracy, export rows from the notebook for each model and user.
        """
        seen_ids = {str(x["id"]) for x in user.get("history", []) if "id" in x}
        seed = (int(user["id"]) + sum(ord(c) for c in model_name)) % 997
        model_bias = {
            "Popularity": 0.08,
            "Neural Matrix Factorization": 0.06,
            "LightFM WARP": 0.045,
            "Graph Embeddings": 0.035,
            "Matrix Factorization SVD": 0.03,
            "User-Based CF": 0.025,
            "Item-Based CF": 0.02,
        }.get(model_name, 0.015)

        candidates = []
        for idx, product in enumerate(self.product_pool):
            if str(product["id"]) in seen_ids:
                continue
            p = deepcopy(product)
            base = float(p.get("score") or 0.35)
            rating = float(p.get("rating") or 3.8) / 5.0
            noise = (((self._id_number(p["id"]) * 31 + seed * 17 + idx) % 100) / 1000.0)
            p["score"] = round(min(0.99, base * 0.55 + rating * 0.35 + model_bias + noise), 6)
            p["why"] = f"Fallback {model_name} score based on exported product quality, user history exclusion, and deterministic ranking."
            candidates.append(p)
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return candidates

    def _rank_and_limit(self, rows: List[Dict[str, Any]], top_k: int, model_name: str) -> List[Dict[str, Any]]:
        normalised = []
        for row in rows:
            p = self._normalise_product(row)
            p["model"] = model_name
            normalised.append(p)
        normalised.sort(key=lambda x: x.get("score", 0), reverse=True)
        for i, row in enumerate(normalised[: int(top_k)], start=1):
            row["rank"] = i
        return normalised[: int(top_k)]

    def similar_users(self, user_id: int, top_k: int = 5) -> Dict[str, Any]:
        user = self.get_user(user_id)
        exact = deepcopy(user.get("similarUsers", []))
        if not exact:
            exact = [
                {"id": uid, "score": round(0.9 - i * 0.05, 3), "reason": "Similar demo profile"}
                for i, uid in enumerate(self.users_by_id.keys())
                if uid != int(user_id)
            ]
        detailed = []
        for row in exact[: int(top_k)]:
            other = self.users_by_id.get(int(row["id"]), {})
            detailed.append({
                "id": int(row["id"]),
                "label": other.get("label", f"User {row['id']}"),
                "persona": other.get("persona", "Similar shopper"),
                "score": row.get("score", 0.0),
                "reason": row.get("reason", "Similar interaction pattern"),
            })
        return {"userId": int(user_id), "similarUsers": detailed}

    def similar_items(self, item_id: Any, top_k: int = 6) -> Dict[str, Any]:
        key = str(item_id)
        rows = deepcopy(self.data.get("similarItems", {}).get(key, []))
        if not rows:
            source = self._find_product(item_id)
            source_category = source.get("category") if source else None
            rows = []
            for p in self.product_pool:
                if str(p["id"]) == str(item_id):
                    continue
                if source_category and p.get("category") != source_category:
                    continue
                q = deepcopy(p)
                q["score"] = round(0.78 - len(rows) * 0.035, 4)
                q["why"] = "Same-category product from the exported product pool."
                rows.append(q)
                if len(rows) >= top_k:
                    break
        return {"itemId": self._clean_id(item_id), "similarItems": self._rank_and_limit(rows, top_k, "Similar Items")}

    def sponsored(self, user_id: Optional[int] = None, top_k: int = 5) -> Dict[str, Any]:
        rows = deepcopy(self.data.get("sponsoredPicks", []))
        for i, row in enumerate(rows):
            row.setdefault("score", round(0.84 - i * 0.04, 4))
            row.setdefault("why", "Sponsored pick matched against the demo user's strongest categories.")
        return {"userId": int(user_id) if user_id is not None else None, "sponsoredPicks": self._rank_and_limit(rows, top_k, "Sponsored")}

    def get_clusters(self) -> List[Dict[str, Any]]:
        return deepcopy(self.data.get("clusters", []))

    def search_products(self, q: str, limit: int = 20) -> Dict[str, Any]:
        query = (q or "").lower().strip()
        if not query:
            return {"query": q, "results": self.product_pool[: int(limit)]}
        matches = []
        for p in self.product_pool:
            text = f"{p.get('title','')} {p.get('category','')} {p.get('why','')}".lower()
            if query in text:
                matches.append(p)
        return {"query": q, "results": matches[: int(limit)]}

    def _find_product(self, item_id: int) -> Optional[Dict[str, Any]]:
        for p in self.product_pool:
            if str(p["id"]) == str(item_id):
                return p
        return None
