import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import argparse

nltk.download('vader_lexicon')

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)['compound']

def add_sentiment(input_csv, output_csv, text_column='text_clean'):
    df = pd.read_csv(input_csv)
    sia = SentimentIntensityAnalyzer()
    df['sentiment_score'] = df[text_column].astype(str).apply(lambda x: sia.polarity_scores(x)['compound'])
    df.to_csv(output_csv, index=False)
    print(f"Sentiment scores saved to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add sentiment scores to Yelp reviews.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV (preprocessed reviews)')
    parser.add_argument('--output', type=str, required=True, help='Path to output CSV (with sentiment)')
    parser.add_argument('--text_column', type=str, default='text_clean', help='Column with cleaned review text')
    args = parser.parse_args()

    add_sentiment(args.input, args.output, args.text_column) 