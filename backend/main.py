from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
logger.info(f"Loading data from: {data_path}")
logger.info(f"File exists: {os.path.exists(data_path)}")

try:
    df = pd.read_csv(data_path)
    logger.info(f"Data loaded successfully! Shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
except Exception as e:
    logger.error(f"Failed to load data: {e}")
    df = pd.DataFrame()  # Empty DataFrame if loading fails

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
    review_count: int = 0
    score: float = 0.0
    similarity_score: float = 0.0

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Yelp Recommendation API is running!"}

@app.post("/recommend", response_model=List[Restaurant])
def recommend(req: RecommendRequest):
    logger.info(f"Recommendation request received: {req.query}")
    
    try:
        if df.empty:
            logger.error("DataFrame is empty - data loading failed")
            raise HTTPException(status_code=500, detail="Data not loaded")
            
        query = req.query.lower()
        logger.info(f"Processing query: '{query}'")
        
        # Simple hardcoded keyword matching
        found_cuisines = [kw for kw in cuisine_keywords if kw in query]
        found_occasions = [kw for kw in occasion_keywords if kw in query]
        
        logger.info(f"Found cuisines: {found_cuisines}")
        logger.info(f"Found occasions: {found_occasions}")
        logger.info(f"Total restaurants in data: {len(df)}")
        
        # Filter by cuisine (categories)
        filtered = df.copy()
        if found_cuisines:
            pattern = '|'.join(found_cuisines)
            logger.info(f"Filtering by pattern: {pattern}")
            
            # Check if categories column exists
            if 'categories' not in df.columns:
                logger.error(f"Categories column not found. Available columns: {list(df.columns)}")
                raise HTTPException(status_code=500, detail="Categories column not found in data")
                
            filtered = filtered[filtered['categories'].str.lower().str.contains(pattern, na=False)]
            logger.info(f"Restaurants after cuisine filter: {len(filtered)}")
        else:
            logger.info("No cuisine keywords found in query")
        
        # Check if required columns exist for sorting
        if 'stars' in df.columns and 'review_count' in df.columns:
            filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
            logger.info("Sorted by stars and review_count")
        elif 'stars' in df.columns:
            filtered = filtered.sort_values('stars', ascending=False)
            logger.info("Sorted by stars only")
        else:
            logger.warning("Stars column not found, no sorting applied")
        
        # Get top 10 unique businesses
        if 'business_id' in df.columns:
            top = filtered.drop_duplicates('business_id').head(10)
            logger.info(f"Final results after deduplication: {len(top)} restaurants")
        else:
            top = filtered.head(10)
            logger.info(f"Final results (no business_id column): {len(top)} restaurants")
        
        # Prepare response
        results = []
        for _, row in top.iterrows():
            try:
                restaurant = Restaurant(
                    name=str(row.get('name', 'Unknown')),
                    address=str(row.get('address', 'No address')),
                    stars=float(row.get('stars', 0.0)),
                    categories=str(row.get('categories', 'No categories')),
                    review_count=int(row.get('review_count', 0)),
                    score=float(row.get('score', 0.0)),
                    similarity_score=float(row.get('similarity_score', 0.0))
                )
                results.append(restaurant)
            except Exception as e:
                logger.warning(f"Error creating restaurant from row: {e}")
                continue
        
        logger.info(f"Returning {len(results)} restaurants")
        return results
        
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {str(e)}")
        logger.error(f"DataFrame columns: {list(df.columns) if not df.empty else 'Empty'}")
        logger.error(f"DataFrame shape: {df.shape}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
