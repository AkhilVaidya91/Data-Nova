import openai
import google.generativeai as gemini
from huggingface_hub import InferenceClient
from pymongo import MongoClient
import os
# import tensorflow as tf
# import tensorflow_hub as hub
# import torch
# from transformers import AutoTokenizer, DistilBertModel
from sentence_transformers import SentenceTransformer

# USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
# USE_MODEL = hub.load(USE_MODULE_URL)

# distilbert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
# distilbert_model = DistilBertModel.from_pretrained("distilbert-base-uncased")

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


# Example usage:
# interface = LLMModelInterface()
# result = interface.call_openai_gpt4_mini(prompt="Hello, world!", api_key="your_openai_api_key")
# print(result)
