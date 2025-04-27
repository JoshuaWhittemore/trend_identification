import pandas as pd
import numpy as np
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
import re

class DataProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.stop_words = set(stopwords.words('english'))
        
    def extract_hashtags(self, text):
        """Extract hashtags from text."""
        if not isinstance(text, str):
            return []
        # Find all hashtags (words starting with #)
        hashtags = re.findall(r'#\w+', text)
        # Remove the # symbol and convert to lowercase
        return [tag[1:].lower() for tag in hashtags]
        
    def load_data(self, file_path):
        """Load the raw data from CSV file."""
        return pd.read_csv(file_path)
    
    def preprocess_text(self, text):
        """Clean and preprocess text data."""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def process_data(self, df):
        """Process the entire dataset."""
        # Try different timestamp parsing approaches
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        except ValueError:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
            except ValueError:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
                except ValueError:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f%z')
        
        # Preprocess text columns
        df['processed_comment'] = df['comment_text'].apply(self.preprocess_text)
        df['processed_caption'] = df['media_caption'].apply(self.preprocess_text)
        
        # Extract hashtags
        df['hashtags'] = df['media_caption'].apply(self.extract_hashtags)
        
        # Extract additional features
        df['comment_length'] = df['comment_text'].str.len()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        return df
    
    def get_basic_stats(self, df):
        """Calculate basic statistics about the dataset."""
        stats = {
            'total_comments': len(df),
            'unique_media': df['media_id'].nunique(),
            'date_range': (df['timestamp'].min(), df['timestamp'].max()),
            'avg_comment_length': df['comment_length'].mean(),
            'comments_per_day': df.groupby(df['timestamp'].dt.date).size().mean(),
            'total_hashtags': sum(len(tags) for tags in df['hashtags']),
            'unique_hashtags': len(set(tag for tags in df['hashtags'] for tag in tags))
        }
        return stats 