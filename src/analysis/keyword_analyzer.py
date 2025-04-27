import pandas as pd
from typing import List, Dict
import time
import re
from collections import Counter
import spacy
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

class KeywordAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        # Common words to exclude
        self.stop_words = set([
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
            'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
            'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
            'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
        ])
        self.max_keywords = 50  # Increased since we're not limited by API calls
        
    def is_valid_keyword(self, word: str) -> bool:
        """Check if a word is valid for keyword analysis."""
        # Must be at least 4 characters
        if len(word) < 4:
            return False
            
        # Must not be a stop word
        if word.lower() in self.stop_words:
            return False
            
        # Must not contain special characters or numbers
        if re.search(r'[^a-zA-Z]', word):
            return False
            
        # Must not be a username (starts with @)
        if word.startswith('@'):
            return False
            
        return True
        
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word using WordNet."""
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word and self.is_valid_keyword(lemma.name()):
                    synonyms.add(lemma.name())
        return list(synonyms)
    
    def get_related_terms(self, word: str, df: pd.DataFrame, text_column: str = 'comment_text') -> List[Dict]:
        """Get terms that frequently co-occur with the given word."""
        # Find sentences containing the word
        sentences = []
        for text in df[text_column]:
            # Convert to string and handle NaN values
            if pd.isna(text):
                continue
            text_str = str(text).lower()
            if word.lower() in text_str:
                sentences.append(text_str)
        
        # Extract words that co-occur
        co_occurring = Counter()
        for sentence in sentences:
            words = word_tokenize(sentence)
            for w in words:
                if self.is_valid_keyword(w) and w != word.lower():
                    co_occurring[w] += 1
        
        # Get top co-occurring terms
        return [{'term': term, 'count': count} for term, count in co_occurring.most_common(10)]
    
    def get_key_phrases(self, word: str, df: pd.DataFrame, text_column: str = 'comment_text') -> List[Dict]:
        """Get key phrases containing the given word."""
        # Find sentences containing the word
        sentences = []
        for text in df[text_column]:
            # Convert to string and handle NaN values
            if pd.isna(text):
                continue
            text_str = str(text).lower()
            if word.lower() in text_str:
                sentences.append(text_str)
        
        # Extract noun phrases using spaCy
        phrases = Counter()
        for sentence in sentences:
            doc = self.nlp(sentence)
            for chunk in doc.noun_chunks:
                if word.lower() in chunk.text.lower():
                    phrases[chunk.text] += 1
        
        return [{'phrase': phrase, 'count': count} for phrase, count in phrases.most_common(10)]
    
    def analyze_keywords_in_corpus(self, df: pd.DataFrame, text_column: str = 'comment_text') -> pd.DataFrame:
        """Analyze keywords in the corpus and find related terms."""
        # Extract unique words from the corpus
        all_words = []
        for text in df[text_column]:
            if pd.isna(text):
                continue
            all_words.extend(str(text).lower().split())
        
        unique_words = set(all_words)
        
        # Filter and sort words by frequency
        word_freq = pd.Series(all_words).value_counts()
        valid_words = [word for word in unique_words if self.is_valid_keyword(word)]
        
        # Sort words by frequency and take top N
        valid_words = sorted(valid_words, key=lambda x: word_freq[x], reverse=True)[:self.max_keywords]
        
        # Get related terms for each valid word
        keyword_analysis = []
        for word in valid_words:
            if word_freq[word] > 5:  # Only analyze words that appear more than 5 times
                print(f"Analyzing keyword: {word} (frequency: {word_freq[word]})")
                
                synonyms = self.get_synonyms(word)
                related_terms = self.get_related_terms(word, df, text_column)
                key_phrases = self.get_key_phrases(word, df, text_column)
                
                keyword_analysis.append({
                    'keyword': word,
                    'frequency': word_freq[word],
                    'synonyms': synonyms,
                    'related_terms': related_terms,
                    'key_phrases': key_phrases
                })
        
        return pd.DataFrame(keyword_analysis) 