import openai
import google.generativeai as gemini
from huggingface_hub import InferenceClient
from pymongo import MongoClient
import os
import numpy as np
from typing import List, Dict
from scipy.spatial.distance import cosine
import re
from collections import Counter
import spacy
# import tensorflow as tf
# import tensorflow_hub as hub
# import torch
# from transformers import AutoTokenizer, DistilBertModel
from sentence_transformers import SentenceTransformer

# USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
# USE_MODEL = hub.load(USE_MODULE_URL)

# distilbert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
# distilbert_model = DistilBertModel.from_pretrained("distilbert-base-uncased")

# NLP = spacy.load("en_core_web_sm")

def clean_think(text):
    """
    Removes text before the "</think>" marker and returns the remaining text.
    If "</think>" is not found, returns an empty string.
    
    :param text: Input text string
    :return: Processed text after "</think>"
    """
    marker = "</think>"
    index = text.find(marker)
    
    if index == -1:
        return ""
    
    return text[index + len(marker):].strip()

minilmm_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class LLMModelInterface:
    def __init__(self):
        """Initialize the LLMModelInterface."""
        pass

    @staticmethod
    def call_openai_gpt4_mini(prompt: str, api_key: str) -> str:
        """Call OpenAI's GPT-4o Mini model."""
        client = openai.OpenAI(api_key = api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                {"role": "developer", "content": "You are an instruction following AI model that behaves and strictly follows the instructions given to you in the prompt."},
                {"role": "user", "content": prompt}
            ],
                max_tokens=8000,
                temperature=0.01
            )
            # print(response.choices[0].message.content.strip())
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            return f"Error calling OpenAI GPT-4o Mini: {e}"

    @staticmethod
    def call_gemini(prompt: str, api_key: str, disable_parse = None) -> str:
        """Call Google's Gemini model via Generative AI API."""
        gemini.configure(api_key=api_key)
        try:
            model = gemini.GenerativeModel("gemini-1.5-flash")
            # print(prompt)
            response = model.generate_content(prompt)
            text = response.text
            # print(text)
            if disable_parse == True:
                return text.strip()
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                result = text[start:end]
                return result.strip()
            else:
                raise ValueError("Model did not return a valid dictionary.")
        except Exception as e:
            print(e)
            return f"Error calling Gemini model: {e}"

    @staticmethod
    def call_gemini_pro(prompt: str, api_key: str, disable_parse = None) -> str:
        """Call Google's Gemini model via Generative AI API."""
        gemini.configure(api_key=api_key)
        try:
            model = gemini.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            text = response.text

            if disable_parse == True:
                return text.strip()
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                result = text[start:end]
                return result.strip()
            else:
                raise ValueError("Model did not return a valid dictionary.")
        except Exception as e:
            print(e)
            return f"Error calling Gemini pro model: {e}"

    @staticmethod
    def call_llama(prompt: str, api_key: str) -> str:
        """Call Llama 3.2 3B model using Hugging Face Transformers."""
        try:

            client = InferenceClient(api_key=api_key)
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            completion = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct", 
                messages=messages, 
                max_tokens=5000,
                temperature=0.01
            )
            print(completion.choices[0].message.content.strip())
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error calling Llama 3.2 3B: {e}"

    @staticmethod
    def call_mistral(prompt: str, api_key: str) -> str:
        """Call Mistral 7B model using Hugging Face Transformers."""
        try:

            client = InferenceClient(api_key=api_key)
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            completion = client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1", 
                messages=messages, 
                # max_tokens=8000,
                temperature=0.01
            )
            # print(completion)
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            return f"Error calling Mistral 7B: {e}"
        
    @staticmethod
    def call_deepseek(prompt: str, api_key: str) -> str:
        """Call DeepSeek R1 model using Hugging Face Transformers."""
        try:

            client = InferenceClient(
                provider="together",
                api_key=api_key
            )
            messages = [
                {
                    "role": "user",
                    "content": prompt + "Do not think too much on the prompt, respond with a relatively lower amount of thought tokens. Also, this is text scraped from a PDF so the sentences might seem a bit incoherent, so dont be too extreme stringent or harsh while deciding if an initiative falls under a particular SDG."
                }
            ]
            completion = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1", 
                messages=messages, 
                max_tokens=50000,
                temperature=0.1
            )
            # print(completion)
            output = completion.choices[0].message.content.strip()
            clean_output = clean_think(output)
            return clean_output
        except Exception as e:
            print(e)
            return f"Error calling DeepSeek: {e}"

    @staticmethod
    def embed_openai(text: str, api_key: str):
        """
        Generate text embeddings using OpenAI's text-embedding-ada-002 model.

        Parameters:
        - text (str): The text string to be embedded.
        - api_key (str): Your OpenAI API key.

        Returns:
        - List[float]: The embedding vector as a list of floats.
        """
        # openai.api_key = api_key
        client = openai.OpenAI(api_key = api_key)
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"OpenAI Embedding Error: {str(e)}")

    @staticmethod
    def embed_gemini(text: str, api_key: str):
        """
        Generate text embeddings using Google's Gemini text-embedding-004 model.

        Parameters:
        - text (str): The text string to be embedded.
        - api_key (str): Your Google Generative AI API key.

        Returns:
        - List[float]: The embedding vector as a list of floats.
        """
        gemini.configure(api_key=api_key)
        try:
            response = gemini.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            return response['embedding']
        except Exception as e:
            raise RuntimeError(f"Gemini Embedding Error: {str(e)}")
        
    @staticmethod
    def embed_use(text: str):
        """
        Generate text embeddings using Google's Universal Sentence Encoder (USE).

        Parameters:
        - text (str): The text string to be embedded.

        Returns:
        - List[float]: The embedding vector as a list of floats.
        """
        try:
            # embeddings = USE_MODEL([text])
            embeddings = []
            embedding = embeddings.numpy().tolist()
            embedding = embedding[0]
            return embedding
        except Exception as e:
            raise RuntimeError(f"USE Embedding Error: {str(e)}")
        
    @staticmethod
    def embed_distilBERT(text):
        """
        Generate embeddings for input text using DistilBERT
        
        Args:
            text (str): Input text to embed
            
        Returns:
            numpy.ndarray: Embedding vector (768 dimensions)
        """
        # tokenizer = distilbert_tokenizer
        # model = distilbert_model

        model = minilmm_model
        
        # inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # with torch.no_grad():
        #     outputs = model(**inputs)

        # embeddings = outputs.last_hidden_state.mean(dim=1)
        # embedding_vector = embeddings.squeeze().numpy().tolist()
        embeddings = model.encode([text])
        embedding_vector = embeddings[0].tolist()
        return embedding_vector

class SentimentAnalyzer:
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Anchor sentences for sentiment
        self.positive_anchors = [
            "The tone of the sentence is positive.",
            "The tone of the sentence is happy."
        ]
        self.negative_anchors = [
            "The tone of the sentence is negative.",
            "The tone of the sentence is sad."
        ]
        
        # Anchor sentences for subjectivity
        self.subjective_anchors = [
            "The sentence expresses an opinion.",
            "The sentence expresses a belief."
        ]
        self.objective_anchors = [
            "The sentence is factual.",
            "The sentence is objective."
        ]
        
        # Pre-compute anchor embeddings
        self.positive_embeddings = self.model.encode(self.positive_anchors)
        self.negative_embeddings = self.model.encode(self.negative_anchors)
        self.subjective_embeddings = self.model.encode(self.subjective_anchors)
        self.objective_embeddings = self.model.encode(self.objective_anchors)
    
    def _compute_similarity_score(self, embedding, anchor_embeddings):
        similarities = [1 - cosine(embedding, anchor) for anchor in anchor_embeddings]
        return np.mean(similarities)
    
    def analyze(self, sentences: List[str]) -> Dict[str, float]:

        if not sentences:
            return {"average_sentiment": 0.0, "average_subjectivity": 0.0}
        # Get embeddings for input sentences
        embeddings = self.model.encode(sentences)
        
        sentiment_scores = []
        subjectivity_scores = []
        
        for embedding in embeddings:
            # Calculate sentiment score (1 = positive, 0 = negative)
            pos_sim = self._compute_similarity_score(embedding, self.positive_embeddings)
            neg_sim = self._compute_similarity_score(embedding, self.negative_embeddings)
            sentiment_score = pos_sim / (pos_sim + neg_sim)
            
            # Calculate subjectivity score (1 = subjective, 0 = objective)
            subj_sim = self._compute_similarity_score(embedding, self.subjective_embeddings)
            obj_sim = self._compute_similarity_score(embedding, self.objective_embeddings)
            subjectivity_score = subj_sim / (subj_sim + obj_sim)
            
            sentiment_scores.append(sentiment_score)
            subjectivity_scores.append(subjectivity_score)
        
        return {
            "average_sentiment": float(np.mean(sentiment_scores)),
            "average_subjectivity": float(np.mean(subjectivity_scores))
        }
    

# Remove references to SpaCy and instead use a simple regex + stopword approach:

class NarcissismAnalyzer:
    def __init__(self):
        # Removed SpaCy usage; define a minimal set of stopwords
        self.stopwords = {
            "the","is","in","and","of","to","a","an","or","that","this",
            "it","be","on","for","with","are","at","by","because","do","did"
        }
        self.narcissistic_indicators = {
            'self_reference': [
                'i', 'me', 'my', 'mine', 'myself',
                'we', 'our', 'ours', 'ourselves'
            ],
            'grandioso_terms': [
                'best', 'greatest',
                'innovative', 'visionary',
                'superior', 'unparalleled'
            ],
            'achievement_terms': [
                'triumph',
                'victory', 'win'
            ],
            'authority_terms': [
                'power', 'influence', 'control',
                'command'
            ]
        }

    def preprocess_text(self, text: str) -> list:
        text = re.sub(r"[^\w\s]", " ", text.lower())  # remove punctuation
        tokens = text.split()
        tokens = [token for token in tokens if token not in self.stopwords]  # remove stopwords
        return tokens

    def analyze_text(self, text: str) -> float:
        if not text or not text.strip():
            return 0.0
        tokens = self.preprocess_text(text)
        scores = {"self_reference": 0.0, "grandioso": 0.0, "achievement": 0.0, "authority": 0.0}
        total_words = len(tokens)
        
        word_counts = Counter(tokens)
        for word, count in word_counts.items():
            if word in self.narcissistic_indicators['self_reference']:
                scores['self_reference'] += count
            if word in self.narcissistic_indicators['grandioso_terms']:
                scores['grandioso'] += count
            if word in self.narcissistic_indicators['achievement_terms']:
                scores['achievement'] += count
            if word in self.narcissistic_indicators['authority_terms']:
                scores['authority'] += count
        
        # Normalize scores and cap at 1.0
        for key in scores:
            if total_words > 0:
                scores[key] = min(scores[key] / total_words * 10, 1.0)
            else:
                scores[key] = 0.0
        
        # Weighted final score
        weights = {
            'self_reference': 0.4,
            'grandioso': 0.3,
            'achievement': 0.15,
            'authority': 0.15
        }
        final_score = sum(scores[k] * weights[k] for k in scores)
        return round(final_score, 3)

def analyze_sentences_narc(sentences):
    """
    Analyze a list of sentences for narcissistic tendencies.
    Returns a single float value between 0 and 1.
    
    Args:
        sentences (list): List of strings, each string being a sentence
        
    Returns:
        float: Narcissism score between 0 and 1
    """
    # Initialize analyzer
    analyzer = NarcissismAnalyzer()
    
    # Combine sentences into single text
    text = ' '.join(sentences)
    
    # Get score
    return analyzer.analyze_text(text)