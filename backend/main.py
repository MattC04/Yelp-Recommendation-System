from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup, transition this later to be api calls to a database
data_path = os.path.join('..', 'output', 'yelp_reviews_bow_sentiment.csv')
df = pd.read_csv(data_path)

# Simple cuisine/occasion keyword lists (expand as needed), this is for initial prototyping, use endpoints to add/remove keywords dynamically
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
    try:
        query = req.query.lower()
        # Simple hardcoded keyword matching
        found_cuisines = [kw for kw in cuisine_keywords if kw in query]
        found_occasions = [kw for kw in occasion_keywords if kw in query]
        
        # Debug info
        print(f"Query: {query}")
        print(f"Found cuisines: {found_cuisines}")
        print(f"Found occasions: {found_occasions}")
        print(f"Total restaurants in data: {len(df)}")
        
        # Filter by cuisine (categories)
        filtered = df.copy()
        if found_cuisines:
            pattern = '|'.join(found_cuisines)
            filtered = filtered[filtered['categories'].str.lower().str.contains(pattern, na=False)]
            print(f"Restaurants after cuisine filter: {len(filtered)}")
        else:
            print("No cuisine keywords found in query")
        
        # Rank by stars and review count
        filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
        
        # Get top 10 unique businesses
        top = filtered.drop_duplicates('business_id').head(10)
        print(f"Final results: {len(top)} restaurants")
        
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
        
    except Exception as e:
        print(f"Error in recommend endpoint: {str(e)}")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"DataFrame shape: {df.shape}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
