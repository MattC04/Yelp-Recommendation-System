from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
import logging
import numpy as np
import hashlib
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
			max_features=10000,
			stop_words='english',
			ngram_range=(1, 2)
		)
		
		logger.info("NLP models initialized successfully")
		return True
	except Exception as e:
		logger.error(f"Failed to initialize NLP models: {e}")
		return False


def _texts_digest(texts: List[str]) -> str:
	m = hashlib.md5()
	for t in texts:
		m.update(t.encode('utf-8'))
	return m.hexdigest()


def process_restaurant_texts(df):
	"""Process restaurant text data for NLP analysis and build caches"""
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
			
		# Create combined text for each restaurant (aligned to df.index order)
		restaurant_texts = []
		for _, row in df.iterrows():
			text_parts = []
			for field in available_fields:
				if pd.notna(row[field]):
					text_parts.append(str(row[field]))
			restaurant_texts.append(' '.join(text_parts))
		
		# Simple on-disk cache for embeddings
		cache_dir = os.path.join('..', 'output', 'nlp_cache')
		os.makedirs(cache_dir, exist_ok=True)
		emb_path = os.path.join(cache_dir, 'embeddings.npy')
		digest_path = os.path.join(cache_dir, 'embeddings.md5')
		current_digest = _texts_digest(restaurant_texts)
		loaded_from_cache = False
		if os.path.exists(emb_path) and os.path.exists(digest_path):
			try:
				with open(digest_path, 'r') as f:
					prev_digest = f.read().strip()
				if prev_digest == current_digest:
					restaurant_embeddings = np.load(emb_path)
					if restaurant_embeddings.shape[0] == len(restaurant_texts):
						loaded_from_cache = True
						logger.info("Loaded embeddings from cache")
			except Exception as e:
				logger.warning(f"Failed loading cached embeddings: {e}")
		
		# Create TF-IDF vectors
		logger.info("Creating TF-IDF vectors...")
		tfidf_matrix = tfidf_vectorizer.fit_transform(restaurant_texts)
		
		# Create sentence embeddings if not cached
		if not loaded_from_cache:
			logger.info("Creating sentence embeddings...")
			restaurant_embeddings = nlp_model.encode(restaurant_texts, show_progress_bar=False)
			try:
				np.save(emb_path, restaurant_embeddings)
				with open(digest_path, 'w') as f:
					f.write(current_digest)
			except Exception as e:
				logger.warning(f"Failed saving embeddings cache: {e}")
		
		logger.info(f"NLP processing complete. TF-IDF shape: {tfidf_matrix.shape}, Embeddings shape: {restaurant_embeddings.shape}")
		return True
		
	except Exception as e:
		logger.error(f"Error in NLP processing: {e}")
		return False


def calculate_semantic_similarity(query: str, indices: Optional[np.ndarray] = None):
	"""Calculate semantic similarity between query and all or selected restaurants"""
	if not NLP_AVAILABLE or nlp_model is None or restaurant_embeddings is None:
		return None
	try:
		query_embedding = nlp_model.encode([query])
		if indices is None:
			emb = restaurant_embeddings
		else:
			emb = restaurant_embeddings[indices]
		return cosine_similarity(query_embedding, emb)[0]
	except Exception as e:
		logger.error(f"Error calculating semantic similarity: {e}")
		return None


def calculate_tfidf_similarity(query: str, indices: Optional[np.ndarray] = None):
	"""Calculate TF-IDF similarity between query and all or selected restaurants"""
	if tfidf_vectorizer is None or tfidf_matrix is None:
		return None
	try:
		query_vector = tfidf_vectorizer.transform([query])
		if indices is None:
			mat = tfidf_matrix
		else:
			mat = tfidf_matrix[indices]
		return cosine_similarity(query_vector, mat)[0]
	except Exception as e:
		logger.error(f"Error calculating TF-IDF similarity: {e}")
		return None

# Load data at startup, transition this later to be api calls to a database
data_path = os.path.join('..', 'output', 'yelp_reviews_bow_sentiment.csv')
logger.info(f"Loading data from: {data_path}")
logger.info(f"File exists: {os.path.exists(data_path)}")

try:
	df = pd.read_csv(data_path)
	# Ensure indices align 0..n-1 with embeddings
	df.reset_index(drop=True, inplace=True)
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

# Simple cuisine/occasion keyword lists (expand as needed)
cuisine_keywords = ['asian', 'chinese', 'japanese', 'korean', 'thai', 'indian', 'italian', 'mexican', 'american', 'french', 'greek', 'mediterranean', 'vietnamese', 'bbq', 'pizza', 'burger', 'seafood', 'sushi']
occasion_keywords = ['family', 'date', 'romantic', 'birthday', 'kids', 'friends', 'business', 'casual', 'fine dining', 'group']


class RecommendRequest(BaseModel):
	query: str
	offset: int = 0  # Number of results to skip for pagination
	limit: int = 25  # Page size
	# Optional weights to tune ranking
	weight_semantic: float = 0.40
	weight_tfidf: float = 0.25
	weight_keyword: float = 0.20
	weight_rating: float = 0.10
	weight_popularity: float = 0.05


class LocationRecommendRequest(BaseModel):
	location: str
	dietary_restrictions: Optional[List[str]] = []
	ambiance: Optional[str] = None
	price_range: Optional[str] = None
	offset: int = 0
	limit: int = 25


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
		if found_cuisines and 'categories' in df.columns:
			pattern = '|'.join(found_cuisines)
			logger.info(f"Filtering by pattern: {pattern}")
			filtered = filtered[filtered['categories'].str.lower().str.contains(pattern, na=False)]
			logger.info(f"Restaurants after cuisine filter: {len(filtered)}")
		else:
			logger.info("No cuisine keywords found in query or 'categories' missing; skipping cuisine filter")
		
		# Check if required columns exist for sorting
		if 'stars' in df.columns and 'review_count' in df.columns:
			filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
		elif 'stars' in df.columns:
			filtered = filtered.sort_values('stars', ascending=False)
		else:
			logger.warning("Stars column not found, no pre-sorting applied")
		
		# Advanced NLP-based ranking system
		if 'business_id' in df.columns:
			# Deduplicate businesses first
			filtered = filtered.drop_duplicates('business_id')
			logger.info(f"Total unique restaurants found: {len(filtered)}")
			
			# Create a scoring frame aligned to filtered rows
			all_results = filtered.copy()
			all_results['semantic_score'] = 0.0
			all_results['tfidf_score'] = 0.0
			all_results['keyword_score'] = 0.0
			all_results['rating_score'] = (all_results['stars'] / 5.0) if 'stars' in all_results.columns else 0.0
			if 'review_count' in all_results.columns:
				max_reviews = max(all_results['review_count'].max(), 1)
				all_results['popularity_score'] = (all_results['review_count'] / max_reviews).fillna(0)
			else:
				all_results['popularity_score'] = 0.0
			
			# Compute similarities on the filtered subset efficiently using aligned indices
			subset_indices = all_results.index.to_numpy()
			sem_scores = calculate_semantic_similarity(query, indices=subset_indices)
			if sem_scores is not None:
				all_results.loc[:, 'semantic_score'] = sem_scores
			else:
				logger.info("Semantic scores unavailable; continuing without")
			
			tfidf_scores = calculate_tfidf_similarity(query, indices=subset_indices)
			if tfidf_scores is not None:
				all_results.loc[:, 'tfidf_score'] = tfidf_scores
			else:
				logger.info("TF-IDF scores unavailable; continuing without")
			
			# Enhanced Keyword Matching Score
			if found_cuisines:
				def _kw_score(row):
					categories_text = str(row.get('categories', '')).lower()
					name_text = str(row.get('name', '')).lower()
					category_matches = sum(1 for kw in found_cuisines if kw in categories_text)
					name_matches = sum(1 for kw in found_cuisines if kw in name_text)
					return ((category_matches * 0.7) + (name_matches * 0.3)) / max(len(found_cuisines), 1)
				all_results['keyword_score'] = all_results.apply(_kw_score, axis=1)
			
			# Weights (normalized just in case)
			weights = np.array([
				req.weight_semantic,
				req.weight_tfidf,
				req.weight_keyword,
				req.weight_rating,
				req.weight_popularity,
			])
			wsum = weights.sum()
			if wsum <= 0:
				weights = np.array([0.40, 0.25, 0.20, 0.10, 0.05])
			else:
				weights = weights / wsum
			
			# Calculate overall score
			all_results['overall_score'] = (
				all_results['semantic_score'] * weights[0] +
				all_results['tfidf_score'] * weights[1] +
				all_results['keyword_score'] * weights[2] +
				all_results['rating_score'] * weights[3] +
				all_results['popularity_score'] * weights[4]
			)
			
			# Sort and paginate
			all_results = all_results.sort_values('overall_score', ascending=False)
			top = all_results.iloc[req.offset:req.offset + req.limit]
			logger.info(f"Returning {len(top)} restaurants with NLP scoring (offset: {req.offset}, limit: {req.limit})")
		else:
			# Fallback for data without business_id
			all_results = filtered
			logger.info(f"Total restaurants found: {len(all_results)}")
			top = all_results.iloc[req.offset:req.offset + req.limit]
			logger.info(f"Returning {len(top)} restaurants (offset: {req.offset}, limit: {req.limit})")
		
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
