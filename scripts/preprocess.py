import re
import string
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import argparse

# Download NLTK data if not already present
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

def clean_text_sentiment_aware(text):
    """Clean text while preserving sentiment-rich features."""
    text = str(text).lower()
    
    # Preserve emotional punctuation patterns
    # Keep multiple exclamation marks, question marks, etc.
    text = re.sub(r'!{2,}', ' !!! ', text)  # Multiple ! -> !!!
    text = re.sub(r'\?{2,}', ' ??? ', text)  # Multiple ? -> ???
    text = re.sub(r'\.{2,}', ' ... ', text)  # Multiple . -> ...
    
    # Preserve emotional repetition (but normalize)
    text = re.sub(r'(\w)\1{3,}', r'\1\1\1', text)  # sooooo -> sooo
    text = re.sub(r'(\w)\1{2,}', r'\1\1', text)    # sooo -> soo
    
    # Remove most punctuation but keep sentiment markers
    text = text.translate(str.maketrans('', '', string.punctuation.replace('!', '').replace('?', '').replace('.', '')))
    
    # Remove numbers but keep emotional numbers
    text = re.sub(r'\b\d+\b', '', text)  # Remove standalone numbers
    text = re.sub(r'\d+', '', text)      # Remove embedded numbers
    
    text = text.strip()
    return text

def preprocess_text_sentiment_aware(text, lemmatize=False):  # Disable lemmatization
    text = clean_text_sentiment_aware(text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    
    # Keep some sentiment-rich stopwords
    sentiment_stopwords = {'not', 'no', 'never', 'always', 'very', 'really', 'so', 'too', 'much', 'many'}
    stop_words = stop_words - sentiment_stopwords
    
    tokens = [w for w in tokens if w not in stop_words and len(w) > 1]  # Reduced min length
    
    # Don't lemmatize to preserve emotional variations
    return ' '.join(tokens)

def preprocess_dataframe_sentiment_aware(df, text_column='text', lemmatize=False):
    df[text_column + '_clean'] = df[text_column].astype(str).apply(lambda x: preprocess_text_sentiment_aware(x, lemmatize=lemmatize))
    return df

def preprocess_chunked_sentiment_aware(input_file, output_file, text_column='text', chunk_size=10000):
    """Process large CSV files in chunks with sentiment-aware preprocessing."""
    
    # Get total number of rows for progress tracking
    print("Counting total rows...")
    total_rows = sum(1 for line in open(input_file, encoding='utf-8')) - 1
    print(f"Total rows: {total_rows:,}")
    
    # Initialize output file with header
    first_chunk = pd.read_csv(input_file, nrows=1)
    first_chunk.to_csv(output_file, index=False)
    
    processed_rows = 0
    chunk_num = 0
    
    # Process in chunks
    for chunk in pd.read_csv(input_file, chunksize=chunk_size):
        chunk_num += 1
        print(f"Processing chunk {chunk_num} ({processed_rows:,}/{total_rows:,} rows processed)")
        
        # Drop rows where the text column is NA
        chunk = chunk.dropna(subset=[text_column])
        
        # Preprocess text with sentiment awareness
        chunk[text_column + '_clean'] = chunk[text_column].astype(str).apply(
            lambda x: preprocess_text_sentiment_aware(x, lemmatize=False)
        )
        
        # Append to output file (without header)
        chunk.to_csv(output_file, mode='a', header=False, index=False)
        
        processed_rows += len(chunk)
        print(f"Completed chunk {chunk_num}. Processed {processed_rows:,}/{total_rows:,} rows")
    
    print(f"Sentiment-aware preprocessing complete! Output saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Yelp review data with sentiment awareness.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV (e.g., data/yelp_reviews.csv)')
    parser.add_argument('--output', type=str, required=True, help='Path to save processed CSV (e.g., output/yelp_reviews_clean_sentiment.csv)')
    parser.add_argument('--text_column', type=str, default='text', help='Name of the text column')
    parser.add_argument('--chunk_size', type=int, default=10000, help='Number of rows to process at once')
    args = parser.parse_args()

    preprocess_chunked_sentiment_aware(args.input, args.output, args.text_column, args.chunk_size) 