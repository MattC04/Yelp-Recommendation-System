import pandas as pd
import os

# Load data
data_path = os.path.join('..', 'output', 'yelp_reviews_bow_sentiment.csv')
print(f"Loading data from: {data_path}")
print(f"File exists: {os.path.exists(data_path)}")

try:
    df = pd.read_csv(data_path)
    print(f"Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"First few rows:")
    print(df.head(3))
    
    # Check if required columns exist
    required_cols = ['name', 'address', 'stars', 'categories', 'business_id']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Missing required columns: {missing_cols}")
    else:
        print("All required columns found!")
        
except Exception as e:
    print(f"Error loading data: {e}") 