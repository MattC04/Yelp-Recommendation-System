import pandas as pd
import numpy as np
from gensim import corpora, models
from gensim.models import LdaModel
from sklearn.feature_extraction.text import CountVectorizer
import argparse
import pickle

def create_lda_model(texts, num_topics=10, passes=15, random_state=42):
    # Create dictionary and corpus
    texts_processed = [text.split() for text in texts if isinstance(text, str) and len(text.split()) > 0]
    dictionary = corpora.Dictionary(texts_processed)
    corpus = [dictionary.doc2bow(text) for text in texts_processed]
    
    # Train LDA model
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=random_state,
        passes=passes,
        alpha='auto',
        per_word_topics=True
    )
    
    return lda_model, dictionary, corpus, texts_processed

def assign_topics_to_reviews(lda_model, corpus, texts_processed):
    topic_assignments = []
    for i, doc in enumerate(corpus):
        doc_topics = lda_model.get_document_topics(doc)
        # Get the topic with highest probability
        dominant_topic = max(doc_topics, key=lambda x: x[1])
        topic_assignments.append(dominant_topic[0])
    return topic_assignments

def get_topic_keywords(lda_model, num_words=10):
    topic_keywords = {}
    for topic_id in range(lda_model.num_topics):
        topic_words = lda_model.show_topic(topic_id, num_words)
        topic_keywords[topic_id] = [word for word, _ in topic_words]
    return topic_keywords

def run_lda_analysis(input_csv, output_csv, text_column='text_clean', num_topics=10, passes=15):
    df = pd.read_csv(input_csv)
    
    # Filter out empty or NaN texts
    df = df.dropna(subset=[text_column])
    texts = df[text_column].astype(str).tolist()
    
    print(f"Running LDA on {len(texts)} reviews with {num_topics} topics...")
    lda_model, dictionary, corpus, texts_processed = create_lda_model(
        texts, num_topics=num_topics, passes=passes
    )
    
    topic_assignments = assign_topics_to_reviews(lda_model, corpus, texts_processed)
    df['topic_id'] = topic_assignments
    topic_keywords = get_topic_keywords(lda_model)
    # Save results
    df.to_csv(output_csv, index=False)
    
    # Save model and topic keywords
    model_path = output_csv.replace('.csv', '_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump({
            'lda_model': lda_model,
            'dictionary': dictionary,
            'topic_keywords': topic_keywords
        }, f)
    
    print(f"LDA results saved to {output_csv}")
    print(f"Model saved to {model_path}")
    print(f"Topic keywords: {topic_keywords}")
    
    return df, lda_model, topic_keywords

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LDA topic modeling on Yelp reviews.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV (e.g., output/yelp_reviews_sentiment.csv)')
    parser.add_argument('--output', type=str, required=True, help='Path to output CSV (e.g., output/yelp_reviews_topics.csv)')
    parser.add_argument('--text_column', type=str, default='text_clean', help='Column with cleaned review text')
    parser.add_argument('--num_topics', type=int, default=10, help='Number of topics to extract')
    parser.add_argument('--passes', type=int, default=15, help='Number of passes for LDA training')
    args = parser.parse_args()

    run_lda_analysis(args.input, args.output, args.text_column, args.num_topics, args.passes) 