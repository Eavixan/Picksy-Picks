```md
# Picksy Picks: Amazon Fashion Recommendation System

Picksy Picks is a full-stack recommendation system demo built for the CSE427 project. The project takes Amazon Fashion review data, processes it into a clean recommendation dataset, compares multiple recommendation algorithms, evaluates them with ranking metrics, and presents the results through an interactive web application.

The goal of this project is to show the complete journey of a recommender system: from raw marketplace data to ranked product suggestions that users can explore in a frontend interface.

## Project Overview

Online marketplaces contain thousands of products, which makes product discovery difficult for users. A recommendation system helps reduce this information overload by ranking products based on user behavior, item relationships, and model scores.

Picksy Picks focuses on Amazon Fashion products and demonstrates:

- Personalized product recommendations
- Multiple recommendation model comparison
- User history and held-out future item visualization
- Similar user discovery
- Similar item recommendations
- Sponsored product suggestions
- Product clusters
- Interactive product details
- Product-type symbols for easier browsing

## Dataset

The original project used Amazon Fashion review and metadata data.

The notebook pipeline scanned approximately:

- 2.5 million raw reviews
- 1.6 million high-quality positive interactions
- 7,259 final filtered interactions
- 2,559 users
- 1,908 metadata items

The data was filtered using rating quality, verified purchase signals, deduplication, k-core filtering, and interaction caps. The final dataset is highly sparse, which makes the recommendation task realistic and challenging.

## Recommendation Models

The project compares several recommendation approaches:

- Popularity baseline
- User-Based Collaborative Filtering
- Item-Based Collaborative Filtering
- Matrix Factorization SVD
- Neural Matrix Factorization
- Graph Embeddings
- LightFM WARP
- LightFM BPR

This allows the project to compare classic, neural, graph-based, and hybrid-ready recommendation methods under the same evaluation setup.

## Evaluation

The system uses a chronological train, validation, and test split to simulate real future user behavior.

Evaluation metrics include:

- HitRate@5
- HitRate@10
- HitRate@20
- NDCG@10
- MRR@10

The final results showed that Popularity performed best on HitRate@10, with Neural Matrix Factorization close behind. This highlights an important recommender-system insight: in very sparse marketplace data, simple popularity-based methods can remain surprisingly strong.

## Web Application

The project includes a full-stack local demo.

### Frontend

The frontend is built with:

- React
- Vite
- CSS
- Lucide React icons

Frontend features include:

- Picksy Picks dashboard
- Demo user selector
- Recommendation model selector
- Top-K recommendation control
- Product search
- Product cards with item-type symbols
- Product detail panel
- Similar item section
- Similar users section
- Sponsored picks section
- Model performance metrics
- Product clusters

### Backend

The backend is built with:

- Python
- FastAPI
- Uvicorn

The backend exposes API endpoints for users, recommendations, model metrics, similar users, similar items, sponsored picks, clusters, and search.

## Data Storage

This demo does not require a live database.

Instead, the recommendation outputs and metadata are stored in:

```text
backend/data/demo-data.json
```

This JSON file acts as a local snapshot of the recommendation system results. It contains project metadata, model metrics, demo users, user histories, recommendations, similar items, sponsored picks, and product clusters.

The models were trained and evaluated in the notebook. The web application uses the exported snapshot so the demo can run quickly and reproducibly without requiring the full raw dataset or database setup.

In a production version, this JSON snapshot could be replaced with PostgreSQL, MongoDB, Firebase, or another database.

## Project Structure

```text
recommender-fullstack-local/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── recommender_service.py
│   ├── data/
│   │   └── demo-data.json
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
│
├── notebook/
│   └── final_recommendation_uploaded.ipynb
│
├── final_recommendation.ipynb
├── start-backend.bat
├── start-frontend.bat
├── package.json
└── README.md
```

## How to Run Locally

### 1. Install dependencies

From the project root:

```bash
npm install
```

### 2. Start the backend

On Windows:

```bash
start-backend.bat
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### 3. Start the frontend

On Windows:

```bash
start-frontend.bat
```

The frontend runs at:

```text
http://127.0.0.1:4173
```

### 4. Run both together

You can also run:

```bash
npm run start
```

## Important API Endpoints

```text
GET /api/health
GET /api/bootstrap
GET /api/models
GET /api/users
GET /api/users/{user_id}
GET /api/users/{user_id}/history
GET /api/recommendations
GET /api/similar-users/{user_id}
GET /api/similar-items/{item_id}
GET /api/sponsored
GET /api/clusters
GET /api/search
```

## Demo Workflow

A good demonstration flow is:

1. Open Picksy Picks in the browser.
2. Show the dataset summary cards.
3. Select different demo users.
4. Explain user history and held-out future items.
5. Switch between recommendation models.
6. Change the Top-K value.
7. Click a product card to open product details.
8. Show recommendation score, rating, price, and explanation.
9. Show how “More Like This” changes based on the selected product.
10. Search for products such as `necklace`, `charm`, or `silver`.
11. Show similar users and sponsored picks.
12. Compare model performance metrics.
13. Finish with product clusters and future scope.

## Future Scope

Possible improvements include:

- Add real product images
- Replace JSON snapshot with a live database
- Store user clicks, saves, and purchases
- Add live feedback-based retraining
- Improve cold-start recommendations using metadata or image/text embeddings
- Deploy frontend and backend online
- Add authentication and real user profiles
- Build a hybrid ranking model combining popularity, neural scores, metadata, and recency

## Final Takeaway

Picksy Picks demonstrates a complete recommendation system prototype. It connects data preprocessing, model training, evaluation, backend APIs, and an interactive frontend into one working system.

The project shows not only how recommendations are generated, but also how they can be evaluated, compared, explained, and demonstrated through a usable web interface.
```
