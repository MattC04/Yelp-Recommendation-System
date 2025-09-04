# Yelp Recommendation System

A full-stack recommendation app that ranks restaurants using reviews, sentiment, and NLP semantics, with a Vue frontend and a FastAPI backend.

## Overview
- Frontend: Vue (`frontend/src/components/YelpSearch.vue`) with a dual-field search (Find + Near), result ranking and explanations, loading animation, optional map view, and minimal AI scoring fallback in the UI.
- Backend: FastAPI (`backend/main.py`) that loads the processed Yelp dataset, computes TF‑IDF and (optionally) SentenceTransformer semantic similarities, and exposes a unified `/search` endpoint.
- Data: Main raw reviews live in `data/yelp_reviews.csv` (large). A processed, smaller file with sentiment and bag-of-words lives in `output/yelp_reviews_bow_sentiment.csv` and is used for fast search.

## Data & Models
- Dataset used at runtime: `output/yelp_reviews_bow_sentiment.csv` (10k rows sampled + engineered columns)
  - Important columns: `name`, `address`, `city`, `state`, `postal_code`, `stars`, `review_count`, `categories`, `text` (review), `text_bow` (bag-of-words), `sentiment` (precomputed score)
- Models/Representations:
  - TF‑IDF (scikit-learn): built over concatenated text fields (`name`, `categories`, `address` or reviews) for lexical similarity.
  - SentenceTransformer (optional): `all-MiniLM-L6-v2` for semantic similarity; falls back to non-NLP when not available.
  - Keyword features: direct regex contains across `categories`, `text`, `text_bow`, `name`.

## Backend API (FastAPI)
File: `backend/main.py`

- Health: `GET /health` — status, data shape, NLP availability
- Unified Search: `POST /search`
  - Request body:
    ```json
    {
      "query": "asian",      // optional
      "location": "New York",// optional
      "offset": 0,
      "limit": 25,
      "weight_semantic": 0.40,
      "weight_tfidf": 0.30,
      "weight_keyword": 0.15,
      "weight_rating": 0.10,
      "weight_popularity": 0.05
    }
    ```
  - Response: array of restaurants with fields:
    - `name`, `address`, `stars`, `categories`, `review_count`
    - Scores: `score` (UI), `overall_score`, `semantic_score`, `tfidf_score`, `keyword_score`, `rating_score`, `popularity_score`
    - Location: `latitude`, `longitude` (if present in data)

### Ranking Pipeline (Backend)
1. Optional location filter across `address`, `city`, `state`, `postal_code` (case-insensitive substring).
2. Query processing:
   - TF‑IDF similarity for lexical match
   - Semantic similarity (if SentenceTransformer loaded)
   - Keyword OR-match across `categories`, `text`, `text_bow`, `name`
3. Normalize and combine scores using weights:
   - `overall = w_sem*semantic + w_tfidf*tfidf + w_kw*keyword + w_rating*rating + w_pop*popularity`
4. Sort by `(overall desc, stars desc, review_count desc)`
5. Deduplicate by `(name, address)`
6. Paginate and return typed response

### Tuning Weights (Environment)
Set any of the following to override request defaults (optional):
- `SEARCH_WEIGHT_SEMANTIC`
- `SEARCH_WEIGHT_TFIDF`
- `SEARCH_WEIGHT_KEYWORD`
- `SEARCH_WEIGHT_RATING`
- `SEARCH_WEIGHT_POPULARITY`

If unset, request-provided defaults are used.

## Frontend Flow (Vue)
File: `frontend/src/components/YelpSearch.vue`

1. User types Find (query) and Near (location); clicks Search.
2. Inputs validated and sanitized (`securityService`).
3. `POST /search` with `query` and `location`.
4. Results render with a loading animation while awaiting response.
5. UI applies an optional AI scoring via `aiRecommender.scoreAndExplain` and falls back to star-based scoring if it fails.
6. Sorting options (AI Score, Rating, Popularity) reorder the displayed list client-side.

### Map Search
- Toggle between List and Map views using the buttons in `YelpSearch.vue`.
- The Map view uses `frontend/src/components/MapResults.vue` (Leaflet via CDN) to plot markers for results that include `latitude` and `longitude`.
- The map will auto-fit to visible markers. If your dataset lacks coordinates, markers will be sparse; consider enriching data or adding geocoding.

## How to Run (Development)
Backend (PowerShell on Windows):
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Verify:
```powershell
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

Frontend:
```powershell
cd frontend
npm install
npm run dev
```
Open the dev URL printed by Vite (usually `http://localhost:5173`).

## Troubleshooting
- "Method Not Allowed": ensure the frontend calls `POST /search` (not a GET) and backend is running on `:8000`.
- Empty results:
  - Try query without location; then try a different term (e.g., "sushi").
  - Confirm `/health` shows `data_loaded: true` and `nlp_available`.
  - Loosen weights by lowering semantic if embeddings aren’t loaded.
- CORS: backend allows `http://localhost:5173` by default.

## Project Structure
```
backend/
  main.py            # FastAPI app with /search
  check_data.py      # Data sanity checks
frontend/
  src/components/YelpSearch.vue  # Search UI (List/Map toggle)
  src/components/MapResults.vue  # Leaflet map for results
  src/services/aiRecommender.js  # Optional UI scoring
  src/services/securityService.js
output/
  yelp_reviews_bow_sentiment.csv # Processed file used by backend
data/
  yelp_reviews.csv                # Original reviews (large)
```

## Notes
- If SentenceTransformer isn’t installed, backend falls back to TF‑IDF/keyword/rating/popularity and still works.
- The UI scoring is best-effort; failures fall back to rating-based order to keep the app usable.
