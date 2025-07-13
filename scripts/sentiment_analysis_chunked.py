import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import argparse

nltk.download('vader_lexicon')

def add_sentiment_chunked(input_csv, output_csv, text_column='text_clean', chunk_size=10000):
    """Add sentiment scores to large CSV files in chunks."""
    
    # Get total number of rows for progress tracking
    print("Counting total rows...")
    total_rows = sum(1 for line in open(input_csv, encoding='utf-8')) - 1
    print(f"Total rows: {total_rows:,}")
    
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Initialize output file with header
    first_chunk = pd.read_csv(input_csv, nrows=1)
    first_chunk['sentiment_score'] = 0.0  # Add sentiment column
    first_chunk.to_csv(output_csv, index=False)
    
    processed_rows = 0
    chunk_num = 0
    
    # Process in chunks
    for chunk in pd.read_csv(input_csv, chunksize=chunk_size):
        chunk_num += 1
        print(f"Processing chunk {chunk_num} ({processed_rows:,}/{total_rows:,} rows processed)")
        
        # Add sentiment scores
        chunk['sentiment_score'] = chunk[text_column].astype(str).apply(
            lambda x: sia.polarity_scores(x)['compound']
        )
        
        # Append to output file (without header)
        chunk.to_csv(output_csv, mode='a', header=False, index=False)
        
        processed_rows += len(chunk)
        print(f"Completed chunk {chunk_num}. Processed {processed_rows:,}/{total_rows:,} rows")
    
    print(f"Sentiment analysis complete! Output saved to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add sentiment scores to Yelp reviews in chunks.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV (e.g., output/yelp_reviews_clean.csv)')
    parser.add_argument('--output', type=str, required=True, help='Path to output CSV (e.g., output/yelp_reviews_sentiment.csv)')
    parser.add_argument('--text_column', type=str, default='text_clean', help='Column with cleaned review text')
    parser.add_argument('--chunk_size', type=int, default=10000, help='Number of rows to process at once')
    args = parser.parse_args()

    add_sentiment_chunked(args.input, args.output, args.text_column, args.chunk_size) 