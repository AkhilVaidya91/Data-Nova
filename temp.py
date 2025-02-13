from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
import torch

class SentimentAnalyzer:
    """
    A class that provides sentiment and subjectivity analysis using different transformer models.
    Supports both sentence-transformers and smaller language models.
    """
    
    def __init__(self, model_type: str = "distilbert"):
        """
        Initialize the sentiment analyzer with specified model type.
        
        Args:
            model_type (str): Type of model to use ('distilbert', 'roberta', 'sentence-transformer')
        """
        self.model_type = model_type
        
        if model_type == "distilbert":
            # Initialize sentiment analysis pipeline
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
            
            # Initialize subjectivity pipeline
            self.subjectivity_model = pipeline(
                "text-classification",
                model="textattack/distilbert-base-uncased-SST-2",
                return_all_scores=True
            )
            
        elif model_type == "roberta":
            # Initialize RoBERTa model for sentiment
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="roberta-base",
                return_all_scores=True
            )
            
            # Initialize RoBERTa model for subjectivity
            self.subjectivity_model = pipeline(
                "text-classification",
                model="roberta-base",
                return_all_scores=True
            )
            
        elif model_type == "sentence-transformer":
            # Initialize SentenceTransformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
        else:
            raise ValueError("Unsupported model type. Choose 'distilbert', 'roberta', or 'sentence-transformer'")
    
    def analyze_sentiment_distilbert_roberta(self, sentences: List[str]) -> Tuple[float, float]:
        """
        Analyze sentiment and subjectivity using DistilBERT or RoBERTa models.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Tuple containing average sentiment score and average subjectivity score
        """
        sentiment_scores = []
        subjectivity_scores = []
        
        for sentence in sentences:
            # Get sentiment scores
            sentiment_result = self.sentiment_model(sentence)[0]
            pos_score = next(score['score'] for score in sentiment_result if score['label'] == 'POSITIVE')
            sentiment_scores.append(pos_score)
            
            # Get subjectivity scores
            subjectivity_result = self.subjectivity_model(sentence)[0]
            subj_score = next(score['score'] for score in subjectivity_result if score['label'] == 'LABEL_1')
            subjectivity_scores.append(subj_score)
        
        avg_sentiment = np.mean(sentiment_scores)
        avg_subjectivity = np.mean(subjectivity_scores)
        
        return avg_sentiment, avg_subjectivity
    
    def analyze_sentiment_sentence_transformer(self, sentences: List[str]) -> Tuple[float, float]:
        """
        Analyze sentiment and subjectivity using SentenceTransformer model.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Tuple containing average sentiment score and average subjectivity score
        """
        # Encode sentences to get embeddings
        embeddings = self.model.encode(sentences)
        
        # Calculate sentiment scores (using the first dimension as proxy for sentiment)
        sentiment_scores = [embedding[0] for embedding in embeddings]
        
        # Calculate subjectivity scores (using the second dimension as proxy for subjectivity)
        subjectivity_scores = [embedding[1] for embedding in embeddings]
        
        # Normalize scores to [0, 1] range
        sentiment_scores = (sentiment_scores - np.min(sentiment_scores)) / (np.max(sentiment_scores) - np.min(sentiment_scores))
        subjectivity_scores = (subjectivity_scores - np.min(subjectivity_scores)) / (np.max(subjectivity_scores) - np.min(subjectivity_scores))
        
        avg_sentiment = np.mean(sentiment_scores)
        avg_subjectivity = np.mean(subjectivity_scores)
        
        return avg_sentiment, avg_subjectivity
    
    def analyze(self, sentences: List[str]) -> Dict[str, float]:
        """
        Main method to analyze sentences using the selected model type.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Dictionary containing average sentiment and subjectivity scores
        """
        if self.model_type in ["distilbert", "roberta"]:
            avg_sentiment, avg_subjectivity = self.analyze_sentiment_distilbert_roberta(sentences)
        else:
            avg_sentiment, avg_subjectivity = self.analyze_sentiment_sentence_transformer(sentences)
            
        return {
            "average_sentiment": float(avg_sentiment),
            "average_subjectivity": float(avg_subjectivity)
        }
    

# from sentiment_analyzer import SentimentAnalyzer
import pandas as pd
from typing import Dict
import time

def format_results(results: Dict[str, float]) -> str:
    """Format the results with proper rounding"""
    return f"Sentiment: {results['average_sentiment']:.3f}, Subjectivity: {results['average_subjectivity']:.3f}"

def test_sentiment_analyzer():
    # Test sentences covering different types of content
    test_sentences = [
        "I absolutely love this new smartphone, it's amazing!",  # Very positive, subjective
        "The weather today is 75 degrees Fahrenheit.",          # Neutral, objective
        "This movie was terrible and a complete waste of time.", # Very negative, subjective
        "Water boils at 100 degrees Celsius.",                  # Neutral, objective
        "I think the restaurant's service could be better.",    # Slightly negative, subjective
        "The Earth completes one rotation every 24 hours.",     # Neutral, objective
        "This is the best day of my life!",                    # Very positive, subjective
        "The package was delivered yesterday at noon."          # Neutral, objective
    ]

    # Initialize analyzers for each model type
    models = {
        "DistilBERT": SentimentAnalyzer(model_type="distilbert"),
        "RoBERTa": SentimentAnalyzer(model_type="roberta"),
        "Sentence-Transformer": SentimentAnalyzer(model_type="sentence-transformer")
    }

    # Store results for comparison
    all_results = []

    # Test each model
    for model_name, analyzer in models.items():
        print(f"\nTesting {model_name} model...")
        start_time = time.time()
        
        # Analyze all sentences
        results = analyzer.analyze(test_sentences)
        
        # Store overall results
        all_results.append({
            "Model": model_name,
            "Average Sentiment": results["average_sentiment"],
            "Average Subjectivity": results["average_subjectivity"],
            "Processing Time": f"{time.time() - start_time:.2f}s"
        })
        
        # Analyze individual sentences
        print(f"\n{model_name} - Individual Sentence Analysis:")
        for i, sentence in enumerate(test_sentences, 1):
            individual_result = analyzer.analyze([sentence])
            print(f"\nSentence {i}: \"{sentence}\"")
            print(f"Scores: {format_results(individual_result)}")

    # Create comparison DataFrame
    comparison_df = pd.DataFrame(all_results)
    print("\nModel Comparison:")
    print(comparison_df.to_string(index=False))

if __name__ == "__main__":
    print("Starting Sentiment Analysis Test...")
    test_sentiment_analyzer()