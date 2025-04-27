import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import Counter
import spacy
from datetime import datetime, timedelta
import re

class TrendAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.lda = LatentDirichletAllocation(n_components=5, random_state=42)
        
        # Simple sentiment word lists
        self.positive_words = set(['good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'wonderful', 'fantastic', 'awesome'])
        self.negative_words = set(['bad', 'poor', 'terrible', 'worst', 'hate', 'awful', 'horrible', 'disappointing', 'useless', 'waste'])
        
    def extract_keywords(self, text):
        """Extract key phrases from text using spaCy."""
        doc = self.nlp(text)
        keywords = []
        for chunk in doc.noun_chunks:
            keywords.append(chunk.text.lower())
        return keywords
    
    def identify_trends(self, df, time_window='1D'):
        """Identify trends over time."""
        # Group by time window
        df['time_window'] = pd.Grouper(key='timestamp', freq=time_window)
        grouped = df.groupby('time_window')
        
        trends = []
        for window, group in grouped:
            # Extract keywords from comments
            all_keywords = []
            for comment in group['processed_comment']:
                all_keywords.extend(self.extract_keywords(comment))
            
            # Count keyword frequencies
            keyword_counts = Counter(all_keywords)
            
            # Get top keywords
            top_keywords = keyword_counts.most_common(10)
            
            trends.append({
                'window': window,
                'top_keywords': top_keywords,
                'comment_count': len(group)
            })
        
        return pd.DataFrame(trends)
    
    def perform_topic_modeling(self, df):
        """Perform LDA topic modeling on comments."""
        # Create document-term matrix
        dtm = self.vectorizer.fit_transform(df['processed_comment'])
        
        # Fit LDA model
        lda_output = self.lda.fit_transform(dtm)
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract top words for each topic
        topics = []
        for topic_idx, topic in enumerate(self.lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-10-1:-1]]
            topics.append({
                'topic_id': topic_idx,
                'top_words': top_words
            })
        
        return topics
    
    def analyze_sentiment(self, df):
        """Analyze sentiment trends over time using a simple word-based approach."""
        sentiments = []
        for comment in df['processed_comment']:
            # Count positive and negative words
            words = comment.lower().split()
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            # Calculate sentiment score
            total_words = len(words)
            if total_words > 0:
                sentiment_score = (positive_count - negative_count) / total_words
            else:
                sentiment_score = 0
            sentiments.append(sentiment_score)
        
        df['sentiment_score'] = sentiments
        return df.groupby(pd.Grouper(key='timestamp', freq='1D'))['sentiment_score'].mean() 