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
import sqlite3
import time

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

# ---------------------------
# SQLite Event Store (Light)
# ---------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), 'events.db')

def get_db():
	conn = sqlite3.connect(DB_PATH, check_same_thread=False)
	conn.execute("PRAGMA journal_mode=WAL;")
	conn.row_factory = sqlite3.Row
	return conn

def init_db():
	conn = get_db()
	conn.execute(
		"""
		CREATE TABLE IF NOT EXISTS events (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			ts INTEGER NOT NULL,
			type TEXT NOT NULL,
			restaurant_name TEXT,
			cuisine TEXT,
			session_id TEXT,
			user_id TEXT
		);
		"""
	)
	conn.commit()
	conn.close()

@app.on_event("startup")
def on_startup():
	try:
		init_db()
		logger.info(f"SQLite event store initialized at {DB_PATH}")
	except Exception as e:
		logger.error(f"Failed to initialize DB: {e}")

class EventIn(BaseModel):
	type: str  # 'click' | 'view' | 'positive' | 'negative' | 'save'
	restaurantName: Optional[str] = None
	cuisine: Optional[str] = None
	sessionId: Optional[str] = None
	userId: Optional[str] = None
	ts: Optional[int] = None  # epoch ms

class EventsIn(BaseModel):
	events: List[EventIn]

@app.post("/events")
def ingest_events(payload: EventsIn):
	try:
		conn = get_db()
		cur = conn.cursor()
		rows = []
		for e in payload.events:
			ts = e.ts if e.ts is not None else int(time.time() * 1000)
			rows.append((ts, e.type, (e.restaurantName or '')[:256], (e.cuisine or '')[:256], (e.sessionId or '')[:128], (e.userId or '')[:128]))
		cur.executemany(
			"INSERT INTO events (ts, type, restaurant_name, cuisine, session_id, user_id) VALUES (?,?,?,?,?,?)",
			rows
		)
		conn.commit()
		return {"status": "ok", "inserted": len(rows)}
	except Exception as e:
		logger.error(f"Failed to ingest events: {e}")
		raise HTTPException(status_code=500, detail="Failed to ingest events")
	finally:
		try:
			conn.close()
		except Exception:
			pass

@app.get("/events/aggregate")
def aggregate_events(half_life_hours: int = 72):
	"""Return decayed positive/negative cuisine weights and basic CTR."""
	try:
		conn = get_db()
		cur = conn.cursor()
		cur.execute("SELECT ts, type, cuisine FROM events WHERE cuisine IS NOT NULL AND cuisine != ''")
		rows = cur.fetchall()
		now = int(time.time() * 1000)
		lam = np.log(2) / (half_life_hours * 3600 * 1000)
		cuisine_pos = {}
		cuisine_neg = {}
		clicks = 0.0
		views = 0.0
		for r in rows:
			age = max(0, now - int(r[0]))
			w = float(np.exp(-lam * age))
			t = r[1]
			c = str(r[2]).lower()
			if t in ("positive", "save"):
				cuisine_pos[c] = cuisine_pos.get(c, 0.0) + w
			elif t == "negative":
				cuisine_neg[c] = cuisine_neg.get(c, 0.0) + w
			elif t == "click":
				clicks += w
			elif t == "view":
				views += w
		ctr = (clicks / views) if views > 0 else 0.0
		return {"cuisinePos": cuisine_pos, "cuisineNeg": cuisine_neg, "ctr": ctr, "count": len(rows)}
	except Exception as e:
		logger.error(f"Failed to aggregate events: {e}")
		raise HTTPException(status_code=500, detail="Failed to aggregate events")
	finally:
		try:
			conn.close()
		except Exception:
			pass

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


class CombinedRecommendRequest(BaseModel):
	query: Optional[str] = None
	location: str
	dietary_restrictions: Optional[List[str]] = []
	ambiance: Optional[str] = None
	price_range: Optional[str] = None
	offset: int = 0
	limit: int = 25


class SearchRequest(BaseModel):
	query: Optional[str] = None
	location: Optional[str] = None
	offset: int = 0
	limit: int = 25
	# weights
	weight_semantic: float = 0.40
	weight_tfidf: float = 0.30
	weight_keyword: float = 0.15
	weight_rating: float = 0.10
	weight_popularity: float = 0.05


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
	latitude: Optional[float] = None
	longitude: Optional[float] = None


@app.get("/")
def read_root():
	logger.info("Root endpoint called")
	return {"message": "Yelp Recommendation API is running!"}


@app.get("/health")
def health_check():
	"""Health check endpoint to verify API and data status"""
	try:
		status = {
			"status": "healthy",
			"timestamp": pd.Timestamp.now().isoformat(),
			"data_loaded": not df.empty,
			"data_shape": df.shape if not df.empty else None,
			"data_columns": list(df.columns) if not df.empty else [],
			"nlp_available": NLP_AVAILABLE,
			"nlp_initialized": nlp_model is not None
		}
		logger.info("Health check completed successfully")
		return status
	except Exception as e:
		logger.error(f"Health check failed: {e}")
		return {
			"status": "unhealthy",
			"error": str(e),
			"timestamp": pd.Timestamp.now().isoformat()
		}


@app.get("/debug/data")
def debug_data():
	"""Debug endpoint to inspect data structure and sample values"""
	try:
		if df.empty:
			return {"error": "DataFrame is empty"}
		
		# Get sample data from each column
		sample_data = {}
		for col in df.columns:
			if col in ['address', 'city', 'state', 'name', 'categories']:
				non_null_values = df[col].dropna()
				if len(non_null_values) > 0:
					sample_data[col] = {
						"total_values": len(df[col]),
						"non_null_values": len(non_null_values),
						"sample_values": non_null_values.head(10).tolist(),
						"unique_values": non_null_values.nunique()
					}
		
		return {
			"data_shape": df.shape,
			"columns": list(df.columns),
			"sample_data": sample_data
		}
	except Exception as e:
		logger.error(f"Debug data endpoint failed: {e}")
		return {"error": str(e)}


@app.get("/test/location/{search_term}")
def test_location_search(search_term: str):
	"""Test endpoint to see what location search would find"""
	try:
		if df.empty:
			return {"error": "DataFrame is empty"}
		
		search_term_lower = search_term.lower()
		results = {}
		
		# Check each possible location column
		possible_location_columns = ['address', 'city', 'state', 'zip', 'zipcode', 'postal_code', 'location']
		
		for col in df.columns:
			col_lower = col.lower()
			if any(loc_col in col_lower for loc_col in possible_location_columns):
				# Check for exact matches
				exact_matches = df[df[col].astype(str).str.lower().str.contains(search_term_lower, na=False, regex=False)]
				results[col] = {
					"exact_matches": len(exact_matches),
					"sample_values": exact_matches[col].dropna().head(5).tolist() if len(exact_matches) > 0 else [],
					"all_unique_values": df[col].dropna().unique().tolist()[:20]  # Show first 20 unique values
				}
		
		return {
			"search_term": search_term,
			"results": results,
			"total_restaurants": len(df)
		}
	except Exception as e:
		logger.error(f"Test location search failed: {e}")
		return {"error": str(e)}


@app.get("/test/simple")
def test_simple():
	"""Simple test endpoint to verify basic functionality"""
	try:
		if df.empty:
			return {"error": "DataFrame is empty", "status": "no_data"}
		
		# Just return the first few restaurants
		sample_data = df.head(5)[['name', 'address', 'stars']].to_dict('records')
		
		return {
			"status": "working",
			"total_restaurants": len(df),
			"sample_data": sample_data,
			"columns": list(df.columns)
		}
	except Exception as e:
		logger.error(f"Simple test failed: {e}")
		return {"error": str(e), "status": "error"}


@app.post("/recommend-by-location", response_model=List[Restaurant])
def recommend_by_location(req: LocationRecommendRequest):
	logger.info(f"Location recommendation request received: {req.location}")
	
	try:
		if df.empty:
			logger.error("DataFrame is empty - data loading failed")
			raise HTTPException(status_code=500, detail="Data not loaded")
		
		# Convert location to lowercase for case-insensitive search
		location_query = req.location.lower().strip()
		logger.info(f"Searching for location: '{location_query}'")
		
		# Debug: Show what columns we have
		logger.info(f"Available columns in DataFrame: {list(df.columns)}")
		logger.info(f"DataFrame shape: {df.shape}")
		
		# Filter restaurants by location (search in address, city, state columns)
		filtered = df.copy()
		
		# Check which location columns exist - be more flexible with column names
		location_columns = []
		possible_location_columns = ['address', 'city', 'state', 'zip', 'zipcode', 'postal_code', 'location']
		
		for col in df.columns:
			col_lower = col.lower()
			if any(loc_col in col_lower for loc_col in possible_location_columns):
				location_columns.append(col)
				logger.info(f"Found location column: '{col}' (matches: {[loc_col for loc_col in possible_location_columns if loc_col in col_lower]})")
		
		logger.info(f"Location columns found: {location_columns}")
		
		if not location_columns:
			logger.error("No location columns found in data")
			raise HTTPException(status_code=500, detail="Location data not available")
		
		# Debug: Show sample data from location columns
		for col in location_columns:
			sample_values = df[col].dropna().head(5).tolist()
			logger.info(f"Sample values from '{col}' column: {sample_values}")
		
		# Create location filter mask with improved search logic
		location_mask = pd.Series([False] * len(df), index=df.index)
		
		for col in location_columns:
			col_lower = col.lower()
			
			# Handle different column types with appropriate search logic
			if 'zip' in col_lower or 'postal' in col_lower:
				# ZIP code search - exact match or partial
				zip_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | zip_mask
				logger.info(f"ZIP column '{col}' matches for '{location_query}': {zip_mask.sum()}")
				
			elif 'city' in col_lower:
				# City search - more flexible matching
				city_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | city_mask
				logger.info(f"City column '{col}' matches for '{location_query}': {city_mask.sum()}")
				
			elif 'state' in col_lower:
				# State search - exact or partial matching
				state_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | state_mask
				logger.info(f"State column '{col}' matches for '{location_query}': {state_mask.sum()}")
				
			else:
				# General address/location search
				general_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | general_mask
				logger.info(f"General column '{col}' matches for '{location_query}': {general_mask.sum()}")
		
		filtered = filtered[location_mask]
		logger.info(f"Restaurants found in location '{req.location}': {len(filtered)}")
		
		# Debug: Show some sample matches if any found
		if len(filtered) > 0:
			sample_matches = filtered[['name', 'address'] + [col for col in ['city', 'state'] if col in filtered.columns]].head(3)
			logger.info(f"Sample matches: {sample_matches.to_dict('records')}")
		
		if len(filtered) == 0:
			logger.info(f"No restaurants found in location '{req.location}'")
			# Debug: Try partial matching and show what's available
			logger.info("Trying partial matching...")
			partial_matches = []
			for col in location_columns:
				# Try first 3 characters for partial matching
				if len(location_query) >= 3:
					partial_mask = df[col].astype(str).str.lower().str.contains(location_query[:3], na=False, regex=False)
					partial_values = df[partial_mask][col].dropna().unique().tolist()
					partial_matches.extend(partial_values)
					logger.info(f"Partial matches in '{col}' (first 3 chars): {partial_values[:5]}")
			
			# Also show some random samples from each location column
			logger.info("Random samples from location columns:")
			for col in location_columns:
				random_samples = df[col].dropna().sample(min(5, len(df[col].dropna()))).tolist()
				logger.info(f"Random samples from '{col}': {random_samples}")
			
			return []
		
		# Apply additional filters if provided
		if req.dietary_restrictions:
			logger.info(f"Applying dietary restrictions: {req.dietary_restrictions}")
			dietary_pattern = '|'.join(req.dietary_restrictions)
			filtered = filtered[filtered['categories'].str.lower().str.contains(dietary_pattern, na=False)]
			logger.info(f"Restaurants after dietary filter: {len(filtered)}")
		
		if req.ambiance:
			logger.info(f"Applying ambiance filter: {req.ambiance}")
			# You can expand this with more sophisticated ambiance matching
			ambiance_keywords = {
				'romantic': ['romantic', 'intimate', 'cozy', 'elegant'],
				'casual': ['casual', 'relaxed', 'comfortable', 'laid-back'],
				'family-friendly': ['family', 'kids', 'children', 'playful'],
				'upscale': ['upscale', 'fine dining', 'elegant', 'sophisticated'],
				'outdoor': ['outdoor', 'patio', 'garden', 'terrace'],
				'lively': ['lively', 'energetic', 'vibrant', 'bustling']
			}
			
			if req.ambiance in ambiance_keywords:
				ambiance_pattern = '|'.join(ambiance_keywords[req.ambiance])
				filtered = filtered[filtered['categories'].str.lower().str.contains(ambiance_pattern, na=False)]
				logger.info(f"Restaurants after ambiance filter: {len(filtered)}")
		
		if req.price_range:
			logger.info(f"Applying price range filter: {req.price_range}")
			# You can expand this with actual price data if available
			price_keywords = {
				'budget': ['budget', 'cheap', 'affordable', 'inexpensive'],
				'moderate': ['moderate', 'mid-range', 'reasonable'],
				'expensive': ['expensive', 'luxury', 'high-end', 'premium']
			}
			
			if req.price_range in price_keywords:
				price_pattern = '|'.join(price_keywords[req.price_range])
				filtered = filtered[filtered['categories'].str.lower().str.contains(price_pattern, na=False)]
				logger.info(f"Restaurants after price filter: {len(filtered)}")
		
		# Sort by rating and popularity
		if 'stars' in filtered.columns and 'review_count' in filtered.columns:
			filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
			logger.info("Sorted by stars and review count")
		elif 'stars' in filtered.columns:
			filtered = filtered.sort_values('stars', ascending=False)
			logger.info("Sorted by stars only")
		else:
			logger.warning("No stars column found for sorting")
		
		# Apply pagination
		total_results = len(filtered)
		start_idx = req.offset
		end_idx = min(start_idx + req.limit, total_results)
		paginated_results = filtered.iloc[start_idx:end_idx]
		
		logger.info(f"Pagination: total={total_results}, offset={req.offset}, limit={req.limit}, returning={len(paginated_results)}")
		
		# Debug: Show what we're about to return
		if len(paginated_results) > 0:
			logger.info(f"Sample of results to return:")
			for idx, (_, row) in enumerate(paginated_results.head(3).iterrows()):
				logger.info(f"  {idx+1}. {row.get('name', 'Unknown')} - {row.get('address', 'No address')} - {row.get('stars', 'No stars')} stars")
		else:
			logger.warning("No results to return after pagination!")
		
		# Prepare response
		results = []
		for _, row in paginated_results.iterrows():
			try:
				restaurant = Restaurant(
					name=str(row.get('name', 'Unknown')),
					address=str(row.get('address', 'No address')),
					stars=float(row.get('stars', 0.0)),
					categories=str(row.get('categories', 'No categories')),
					review_count=int(row.get('review_count', 0)),
					score=float(row.get('stars', 0.0)),  # Use stars as base score for location search
					similarity_score=0.0,  # Not applicable for location search
					overall_score=float(row.get('stars', 0.0)),  # Use stars as overall score
					semantic_score=0.0,
					tfidf_score=0.0,
					keyword_score=0.0,
					rating_score=float(row.get('stars', 0.0)) / 5.0,
					popularity_score=float(row.get('review_count', 0)) / max(filtered['review_count'].max(), 1) if 'review_count' in filtered.columns else 0.0
				)
				results.append(restaurant)
				logger.info(f"Created restaurant object: {restaurant.name}")
			except Exception as e:
				logger.warning(f"Error creating restaurant from row: {e}")
				logger.warning(f"Row data: {row.to_dict()}")
				continue
		
		logger.info(f"Successfully created {len(results)} restaurant objects")
		logger.info(f"Successfully returned {len(results)} restaurants for location '{req.location}'")
		return results
		
	except Exception as e:
		logger.error(f"Error in recommend-by-location endpoint: {str(e)}")
		logger.error(f"DataFrame columns: {list(df.columns) if not df.empty else 'Empty'}")
		logger.error(f"DataFrame shape: {df.shape}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/recommend-combined", response_model=List[Restaurant])
def recommend_combined(req: CombinedRecommendRequest):
	logger.info(f"Combined recommendation request received: query='{req.query}', location='{req.location}'")
	
	try:
		if df.empty:
			logger.error("DataFrame is empty - data loading failed")
			raise HTTPException(status_code=500, detail="Data not loaded")
		
		# Convert inputs to lowercase for case-insensitive search
		location_query = req.location.lower().strip()
		cuisine_query = req.query.lower().strip() if req.query else ""
		
		logger.info(f"Searching for cuisine: '{cuisine_query}' in location: '{location_query}'")
		
		# Filter restaurants by location first
		filtered = df.copy()
		location_columns = []
		possible_location_columns = ['address', 'city', 'state', 'zip', 'zipcode', 'postal_code', 'location']
		
		for col in df.columns:
			col_lower = col.lower()
			if any(loc_col in col_lower for loc_col in possible_location_columns):
				location_columns.append(col)
		
		if not location_columns:
			logger.error("No location columns found in data")
			raise HTTPException(status_code=500, detail="Location data not available")
		
		# Create location filter mask with more flexible matching
		location_mask = pd.Series([False] * len(df), index=df.index)
		for col in location_columns:
			col_lower = col.lower()
			if 'zip' in col_lower or 'postal' in col_lower:
				zip_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | zip_mask
			elif 'city' in col_lower:
				city_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | city_mask
			elif 'state' in col_lower:
				state_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | state_mask
			else:
				# For address columns, be more flexible - check if any part contains the location
				general_mask = df[col].astype(str).str.lower().str.contains(location_query, na=False, regex=False)
				location_mask = location_mask | general_mask
		
		# If no exact matches found, try partial matching for better results
		if location_mask.sum() == 0:
			logger.info(f"No exact location matches found for '{location_query}', trying partial matching...")
			for col in location_columns:
				col_lower = col.lower()
				# Try matching first 3+ characters for better partial matching
				if len(location_query) >= 3:
					partial_query = location_query[:3].lower()
					partial_mask = df[col].astype(str).str.lower().str.contains(partial_query, na=False, regex=False)
					location_mask = location_mask | partial_mask
					logger.info(f"Partial match in '{col}' for '{partial_query}': {partial_mask.sum()} matches")
		
		filtered = filtered[location_mask]
		logger.info(f"Restaurants found in location '{req.location}': {len(filtered)}")
		
		# Debug: Show sample matches if any found
		if len(filtered) > 0:
			sample_matches = filtered[['name', 'address'] + [col for col in ['city', 'state'] if col in filtered.columns]].head(3)
			logger.info(f"Sample location matches: {sample_matches.to_dict('records')}")
		
		if len(filtered) == 0:
			logger.info(f"No restaurants found in location '{req.location}'")
			# Try to show what's available in the data
			logger.info("Available cities in data:")
			if 'city' in df.columns:
				city_counts = df['city'].value_counts().head(10)
				logger.info(f"Top cities: {city_counts.to_dict()}")
			return []
		
		# If cuisine query is provided, filter by cuisine as well
		if cuisine_query:
			found_cuisines = [kw for kw in cuisine_keywords if kw in cuisine_query]
			if found_cuisines and 'categories' in filtered.columns:
				pattern = '|'.join(found_cuisines)
				logger.info(f"Filtering by cuisine pattern: {pattern}")
				filtered = filtered[filtered['categories'].str.lower().str.contains(pattern, na=False)]
				logger.info(f"Restaurants after cuisine filter: {len(filtered)}")
		
		# Apply additional filters if provided
		if req.dietary_restrictions:
			logger.info(f"Applying dietary restrictions: {req.dietary_restrictions}")
			dietary_pattern = '|'.join(req.dietary_restrictions)
			filtered = filtered[filtered['categories'].str.lower().str.contains(dietary_pattern, na=False)]
			logger.info(f"Restaurants after dietary filter: {len(filtered)}")
		
		if req.ambiance:
			logger.info(f"Applying ambiance filter: {req.ambiance}")
			ambiance_keywords = {
				'romantic': ['romantic', 'intimate', 'cozy', 'elegant'],
				'casual': ['casual', 'relaxed', 'comfortable', 'laid-back'],
				'family-friendly': ['family', 'kids', 'children', 'playful'],
				'upscale': ['upscale', 'fine dining', 'elegant', 'sophisticated'],
				'outdoor': ['outdoor', 'patio', 'garden', 'terrace'],
				'lively': ['lively', 'energetic', 'vibrant', 'bustling']
			}
			
			if req.ambiance in ambiance_keywords:
				ambiance_pattern = '|'.join(ambiance_keywords[req.ambiance])
				filtered = filtered[filtered['categories'].str.lower().str.contains(ambiance_pattern, na=False)]
				logger.info(f"Restaurants after ambiance filter: {len(filtered)}")
		
		if req.price_range:
			logger.info(f"Applying price range filter: {req.price_range}")
			price_keywords = {
				'budget': ['budget', 'cheap', 'affordable', 'inexpensive'],
				'moderate': ['moderate', 'mid-range', 'reasonable'],
				'expensive': ['expensive', 'luxury', 'high-end', 'premium']
			}
			
			if req.price_range in price_keywords:
				price_pattern = '|'.join(price_keywords[req.price_range])
				filtered = filtered[filtered['categories'].str.lower().str.contains(price_pattern, na=False)]
				logger.info(f"Restaurants after price filter: {len(filtered)}")
		
		# Sort by rating and popularity
		if 'stars' in filtered.columns and 'review_count' in filtered.columns:
			filtered = filtered.sort_values(['stars', 'review_count'], ascending=[False, False])
			logger.info("Sorted by stars and review count")
		elif 'stars' in filtered.columns:
			filtered = filtered.sort_values('stars', ascending=False)
			logger.info("Sorted by stars only")
		else:
			logger.warning("No stars column found for sorting")
		
		# Apply pagination
		total_results = len(filtered)
		start_idx = req.offset
		end_idx = min(start_idx + req.limit, total_results)
		paginated_results = filtered.iloc[start_idx:end_idx]
		
		logger.info(f"Pagination: total={total_results}, offset={req.offset}, limit={req.limit}, returning={len(paginated_results)}")
		
		# Prepare response
		results = []
		for _, row in paginated_results.iterrows():
			try:
				restaurant = Restaurant(
					name=str(row.get('name', 'Unknown')),
					address=str(row.get('address', 'No address')),
					stars=float(row.get('stars', 0.0)),
					categories=str(row.get('categories', 'No categories')),
					review_count=int(row.get('review_count', 0)),
					score=float(row.get('stars', 0.0)),
					similarity_score=0.0,
					overall_score=float(row.get('stars', 0.0)),
					semantic_score=0.0,
					tfidf_score=0.0,
					keyword_score=0.0,
					rating_score=float(row.get('stars', 0.0)) / 5.0,
					popularity_score=float(row.get('review_count', 0)) / max(filtered['review_count'].max(), 1) if 'review_count' in filtered.columns else 0.0
				)
				results.append(restaurant)
				logger.info(f"Created restaurant object: {restaurant.name}")
			except Exception as e:
				logger.warning(f"Error creating restaurant from row: {e}")
				logger.warning(f"Row data: {row.to_dict()}")
				continue
		
		logger.info(f"Successfully created {len(results)} restaurant objects")
		logger.info(f"Successfully returned {len(results)} restaurants for combined search")
		return results
		
	except Exception as e:
		logger.error(f"Error in recommend-combined endpoint: {str(e)}")
		logger.error(f"DataFrame columns: {list(df.columns) if not df.empty else 'Empty'}")
		logger.error(f"DataFrame shape: {df.shape}")
		raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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


@app.post("/search", response_model=List[Restaurant])
def unified_search(req: SearchRequest):
	try:
		if df.empty:
			raise HTTPException(status_code=500, detail="Data not loaded")

		working = df.copy()
		indices = None

		# Optional location filter
		if req.location and req.location.strip():
			location_query = req.location.strip().lower()
			possible_location_columns = ['address', 'city', 'state', 'zip', 'zipcode', 'postal_code', 'location']
			location_columns = [c for c in working.columns if any(k in c.lower() for k in possible_location_columns)]
			if not location_columns:
				logger.warning("No location columns found for /search")
			else:
				mask = pd.Series([False] * len(working), index=working.index)
				for col in location_columns:
					try:
						m = working[col].astype(str).str.lower().str.contains(location_query, na=False)
						mask = mask | m
					except Exception:
						continue
				working = working[mask]
				if len(working) == 0:
					return []
				indices = working.index.to_numpy()

		# Scoring for query
		semantic_scores = None
		tfidf_scores = None
		keyword_scores = None
		if req.query and req.query.strip():
			q = req.query.strip().lower()
			# TF-IDF over combined texts if available
			tfidf_scores = calculate_tfidf_similarity(q, indices=indices)
			# Semantic over embeddings if available
			semantic_scores = calculate_semantic_similarity(q, indices=indices)
			# Simple keyword score against categories and text fields
			kw_series = pd.Series(0.0, index=working.index)
			for col in ['categories', 'text', 'text_bow']:
				if col in working.columns:
					try:
						kw_series = kw_series + working[col].astype(str).str.lower().str.contains(q, na=False).astype(float)
					except Exception:
						pass
			keyword_scores = kw_series.values

		# Build the score
		def _norm(x):
			if x is None: return None
			x = np.array(x, dtype=float)
			if x.size == 0: return x
			mn, mx = np.nanmin(x), np.nanmax(x)
			if mx - mn <= 1e-12: return np.zeros_like(x)
			return (x - mn) / (mx - mn)

		w_sem, w_tfidf, w_kw = req.weight_semantic, req.weight_tfidf, req.weight_keyword
		w_rating, w_pop = req.weight_rating, req.weight_popularity

		s_sem = _norm(semantic_scores)
		s_tfidf = _norm(tfidf_scores)
		s_kw = _norm(keyword_scores)

		# Rating/popularity
		rating = working['stars'].astype(float) if 'stars' in working.columns else pd.Series(0.0, index=working.index)
		pop = working['review_count'].astype(float) if 'review_count' in working.columns else pd.Series(0.0, index=working.index)
		s_rating = _norm(rating.values)
		s_pop = _norm(pop.values)

		overall = np.zeros(len(working))
		if s_sem is not None: overall = overall + w_sem * s_sem
		if s_tfidf is not None: overall = overall + w_tfidf * s_tfidf
		if s_kw is not None: overall = overall + w_kw * s_kw
		overall = overall + w_rating * s_rating + w_pop * s_pop

		working = working.assign(_score=overall,
			semantic_score=(s_sem if s_sem is not None else np.zeros(len(working))),
			tfidf_score=(s_tfidf if s_tfidf is not None else np.zeros(len(working))),
			keyword_score=(s_kw if s_kw is not None else np.zeros(len(working))),
			rating_score=s_rating,
			popularity_score=s_pop,
			overall_score=overall)

		# Prefer higher star/review tie-breakers
		working = working.sort_values(['_score', 'stars', 'review_count'], ascending=[False, False, False], kind='mergesort')

		# De-duplicate by business name/address to avoid multiple review rows
		dedup_cols = [c for c in ['name', 'address'] if c in working.columns]
		if dedup_cols:
			working = working.drop_duplicates(subset=dedup_cols, keep='first')

		# Pagination
		total = len(working)
		start = max(0, req.offset)
		end = min(total, start + max(1, req.limit))
		page = working.iloc[start:end]

		results: List[Restaurant] = []
		for _, row in page.iterrows():
			results.append(Restaurant(
				name=str(row.get('name', 'Unknown')),
				address=str(row.get('address', 'No address')),
				stars=float(row.get('stars', 0.0)),
				categories=str(row.get('categories', 'No categories')),
				review_count=int(row.get('review_count', 0)),
				score=float(row.get('_score', 0.0)),
				similarity_score=float(row.get('semantic_score', 0.0)),
				overall_score=float(row.get('overall_score', 0.0)),
				semantic_score=float(row.get('semantic_score', 0.0)),
				tfidf_score=float(row.get('tfidf_score', 0.0)),
				keyword_score=float(row.get('keyword_score', 0.0)),
				rating_score=float(row.get('stars', 0.0)) / 5.0,
				popularity_score=float(row.get('review_count', 0.0)) / max(float(working['review_count'].max()) if 'review_count' in working.columns else 1.0, 1.0),
				latitude=float(row.get('latitude')) if 'latitude' in working.columns and pd.notna(row.get('latitude')) else None,
				longitude=float(row.get('longitude')) if 'longitude' in working.columns and pd.notna(row.get('longitude')) else None
			))

		return results
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error in /search: {e}")
		raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
