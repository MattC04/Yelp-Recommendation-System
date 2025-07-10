import re
import string
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK data if not already present
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    text = text.strip()
    return text

def preprocess_text(text, lemmatize=True):
    text = clean_text(text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words and len(w) > 2]
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return ' '.join(tokens)

def preprocess_dataframe(df, text_column='text', lemmatize=True):
    df[text_column + '_clean'] = df[text_column].astype(str).apply(lambda x: preprocess_text(x, lemmatize=lemmatize))
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess Yelp review data")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV')
    parser.add_argument('--output', type=str, required=True, help='Path to save processed CSV')
    parser.add_argument('--text_column', type=str, default='text', help='Name of the text column')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    # Drop rows where the text column is NA
    df = df.dropna(subset=[args.text_column])
    df = preprocess_dataframe(df, text_column=args.text_column)
    df.to_csv(args.output, index=False)
    print(f"Processed data saved to {args.output}") 