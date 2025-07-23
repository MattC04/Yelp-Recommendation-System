from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
data_path = os.path.join('output', 'yelp_reviews_bow_sentiment.csv')
df = pd.read_csv(data_path)

# Simple cuisine/occasion keyword lists (expand as needed)
cuisine_keywords = ['asian', 'chinese', 'japanese', 'korean', 'thai', 'indian', 'italian', 'mexican', 'american', 'french', 'greek', 'mediterranean', 'vietnamese', 'bbq', 'pizza', 'burger', 'seafood', 'sushi']
occasion_keywords = ['family', 'date', 'romantic', 'birthday', 'kids', 'friends', 'business', 'casual', 'fine dining', 'group']

class RecommendRequest(BaseModel):
    query: str

class Restaurant(BaseModel):
    name: str
    address: str
    stars: float
    categories: str

@app.get("/")
def read_root():
    return {"message": "Yelp Recommendation API is running!"}

@app.post("/recommend", response_model=List[Restaurant])
def recommend(req: RecommendRequest):
    query = req.query.lower()
    # Find cuisines and occasions in query
    found_cuisines = [kw for kw in cuisine_keywords if kw in query]
    found_occasions = [kw for kw in occasion_keywords if kw in query]
    # Filter by cuisine (categories)
    filtered = df.copy()
    if found_cuisines:
        pattern = '|'.join(found_cuisines)
        filtered = filtered[filtered['categories'].str.lower().str.contains(pattern, na=False)]
    # Optionally, filter by occasion (not implemented, placeholder)
    # For now, just use cuisine filtering
    # Rank by stars and review count
    filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
    # Get top 10 unique businesses
    top = filtered.drop_duplicates('business_id').head(10)
    # Prepare response
    results = [
        Restaurant(
            name=row['name'],
            address=row['address'],
            stars=row['stars'],
            categories=row['categories']
        )
        for _, row in top.iterrows()
    ]
    return results
