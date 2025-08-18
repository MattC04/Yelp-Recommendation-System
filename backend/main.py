from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
import logging
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# NLP imports
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    NLP_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("NLP libraries loaded successfully")
except ImportError:
    NLP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("NLP libraries not available, falling back to keyword matching")

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

# Initialize NLP models
nlp_model = None
tfidf_vectorizer = None
restaurant_embeddings = None
tfidf_matrix = None

def initialize_nlp():
    """Initialize NLP models if available"""
    global nlp_model, tfidf_vectorizer
    
    if not NLP_AVAILABLE:
        logger.warning("NLP not available, using keyword matching only")
        return False
        
    try:
        # Load sentence transformer model (smaller, faster model)
        logger.info("Loading sentence transformer model...")
        nlp_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)  # Unigrams and bigrams
        )
        
        logger.info("NLP models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize NLP models: {e}")
        return False

def process_restaurant_texts(df):
    """Process restaurant text data for NLP analysis"""
    global tfidf_vectorizer, tfidf_matrix, restaurant_embeddings
    
    if not NLP_AVAILABLE or nlp_model is None:
        return False
        
    try:
        # Combine relevant text fields for analysis
        text_fields = ['name', 'categories', 'address']
        available_fields = [field for field in text_fields if field in df.columns]
        
        if not available_fields:
            logger.warning("No text fields available for NLP processing")
            return False
            
        # Create combined text for each restaurant
        restaurant_texts = []
        for _, row in df.iterrows():
            text_parts = []
            for field in available_fields:
                if pd.notna(row[field]):
                    text_parts.append(str(row[field]))
            restaurant_texts.append(' '.join(text_parts))
        
        # Create TF-IDF vectors
        logger.info("Creating TF-IDF vectors...")
        tfidf_matrix = tfidf_vectorizer.fit_transform(restaurant_texts)
        
        # Create sentence embeddings
        logger.info("Creating sentence embeddings...")
        restaurant_embeddings = nlp_model.encode(restaurant_texts, show_progress_bar=False)
        
        logger.info(f"NLP processing complete. TF-IDF shape: {tfidf_matrix.shape}, Embeddings shape: {restaurant_embeddings.shape}")
        return True
        
    except Exception as e:
        logger.error(f"Error in NLP processing: {e}")
        return False

def calculate_semantic_similarity(query, restaurant_embeddings):
    """Calculate semantic similarity between query and restaurants"""
    if not NLP_AVAILABLE or nlp_model is None or restaurant_embeddings is None:
        return None
        
    try:
        # Encode the query
        query_embedding = nlp_model.encode([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, restaurant_embeddings)[0]
        return similarities
        
    except Exception as e:
        logger.error(f"Error calculating semantic similarity: {e}")
        return None

def calculate_tfidf_similarity(query, tfidf_matrix):
    """Calculate TF-IDF similarity between query and restaurants"""
    if tfidf_vectorizer is None or tfidf_matrix is None:
        return None
        
    try:
        # Transform query to TF-IDF vector
        query_vector = tfidf_vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, tfidf_matrix)[0]
        return similarities
        
    except Exception as e:
        logger.error(f"Error calculating TF-IDF similarity: {e}")
        return None

# Load data at startup, transition this later to be api calls to a database
data_path = os.path.join('..', 'output', 'yelp_reviews_bow_sentiment.csv')
logger.info(f"Loading data from: {data_path}")
logger.info(f"File exists: {os.path.exists(data_path)}")

try:
    df = pd.read_csv(data_path)
    logger.info(f"Data loaded successfully! Shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Initialize NLP processing
    if initialize_nlp():
        logger.info("Starting NLP processing...")
        if process_restaurant_texts(df):
            logger.info("NLP processing completed successfully!")
        else:
            logger.warning("NLP processing failed, falling back to keyword matching")
    else:
        logger.info("Using keyword matching only")
        
except Exception as e:
    logger.error(f"Failed to load data: {e}")
    df = pd.DataFrame()  # Empty DataFrame if loading fails

# Simple cuisine/occasion keyword lists (expand as needed), this is for initial prototyping, use endpoints to add/remove keywords dynamically
cuisine_keywords = ['asian', 'chinese', 'japanese', 'korean', 'thai', 'indian', 'italian', 'mexican', 'american', 'french', 'greek', 'mediterranean', 'vietnamese', 'bbq', 'pizza', 'burger', 'seafood', 'sushi']
occasion_keywords = ['family', 'date', 'romantic', 'birthday', 'kids', 'friends', 'business', 'casual', 'fine dining', 'group']

class RecommendRequest(BaseModel):
    query: str
    offset: int = 0  # Number of results to skip for pagination

class Restaurant(BaseModel):
    name: str
    address: str
    stars: float
    categories: str
    review_count: int = 0
    score: float = 0.0
    similarity_score: float = 0.0
    overall_score: float = 0.0
    semantic_score: float = 0.0
    tfidf_score: float = 0.0
    keyword_score: float = 0.0
    rating_score: float = 0.0
    popularity_score: float = 0.0

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
        
        # Advanced NLP-based ranking system
        if 'business_id' in df.columns:
            # Get all unique restaurants
            all_results = filtered.drop_duplicates('business_id')
            logger.info(f"Total unique restaurants found: {len(all_results)}")
            
            # Create a copy for scoring
            all_results = all_results.copy()
            
            # Initialize scores
            all_results['semantic_score'] = 0.0
            all_results['tfidf_score'] = 0.0
            all_results['keyword_score'] = 0.0
            all_results['rating_score'] = 0.0
            all_results['popularity_score'] = 0.0
            
            # 1. Semantic Similarity Score (40% weight)
            if restaurant_embeddings is not None:
                # Get indices of restaurants in the filtered results
                filtered_indices = filtered.index.tolist()
                semantic_similarities = calculate_semantic_similarity(query, restaurant_embeddings)
                
                if semantic_similarities is not None:
                    # Map similarities back to filtered results
                    for idx, row in all_results.iterrows():
                        if idx in filtered_indices:
                            original_idx = filtered_indices.index(idx)
                            all_results.loc[idx, 'semantic_score'] = semantic_similarities[original_idx]
                    
                    logger.info("Semantic similarity scores calculated")
                else:
                    logger.warning("Semantic similarity calculation failed")
            
            # 2. TF-IDF Score (25% weight)
            if tfidf_matrix is not None:
                tfidf_similarities = calculate_tfidf_similarity(query, tfidf_matrix)
                
                if tfidf_similarities is not None:
                    # Map similarities back to filtered results
                    for idx, row in all_results.iterrows():
                        if idx in filtered_indices:
                            original_idx = filtered_indices.index(idx)
                            all_results.loc[idx, 'tfidf_score'] = tfidf_similarities[original_idx]
                    
                    logger.info("TF-IDF similarity scores calculated")
                else:
                    logger.warning("TF-IDF similarity calculation failed")
            
            # 3. Enhanced Keyword Matching Score (20% weight)
            if found_cuisines:
                # More sophisticated keyword matching
                for idx, row in all_results.iterrows():
                    categories_text = str(row.get('categories', '')).lower()
                    name_text = str(row.get('name', '')).lower()
                    
                    # Count keyword matches in categories and name
                    category_matches = sum(1 for kw in found_cuisines if kw in categories_text)
                    name_matches = sum(1 for kw in found_cuisines if kw in name_text)
                    
                    # Weight categories more heavily than name
                    keyword_score = (category_matches * 0.7) + (name_matches * 0.3)
                    all_results.loc[idx, 'keyword_score'] = keyword_score / len(found_cuisines)
            
            # 4. Rating Score (10% weight) - Normalize to 0-1
            all_results['rating_score'] = all_results['stars'] / 5.0
            
            # 5. Popularity Score (5% weight) - Normalize to 0-1
            max_reviews = all_results.get('review_count', 0).max() if 'review_count' in all_results.columns else 1000
            all_results['popularity_score'] = (all_results.get('review_count', 0) / max_reviews).fillna(0)
            
            # Calculate overall score with weights
            all_results['overall_score'] = (
                all_results['semantic_score'] * 0.40 +      # Semantic understanding
                all_results['tfidf_score'] * 0.25 +         # TF-IDF keyword importance
                all_results['keyword_score'] * 0.20 +       # Direct keyword matching
                all_results['rating_score'] * 0.10 +        # Star rating
                all_results['popularity_score'] * 0.05      # Review count
            )
            
            # Sort by overall score
            all_results = all_results.sort_values('overall_score', ascending=False)
            
            # Get results for current page
            top = all_results.iloc[req.offset:req.offset + 25]
            logger.info(f"Returning {len(top)} restaurants with NLP scoring (offset: {req.offset})")
            
        else:
            # Fallback for data without business_id
            all_results = filtered
            logger.info(f"Total restaurants found: {len(all_results)}")
            top = all_results.iloc[req.offset:req.offset + 25]
            logger.info(f"Returning {len(top)} restaurants (offset: {req.offset})")
        
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
                    similarity_score=float(row.get('similarity_score', 0.0)),
                    overall_score=float(row.get('overall_score', 0.0)),
                    semantic_score=float(row.get('semantic_score', 0.0)),
                    tfidf_score=float(row.get('tfidf_score', 0.0)),
                    keyword_score=float(row.get('keyword_score', 0.0)),
                    rating_score=float(row.get('rating_score', 0.0)),
                    popularity_score=float(row.get('popularity_score', 0.0))
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
