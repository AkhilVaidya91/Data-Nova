import google.generativeai as gemini
import requests
from pydantic import BaseModel

class LLMModelInterface:
    def __init__(self):
        """Initialize the LLMModelInterface."""
        pass

    @staticmethod
    def call_gemini(prompt: str, api_key: str, disable_parse = None) -> str:
        """Call Google's Gemini model via Generative AI API."""
        gemini.configure(api_key=api_key)
        try:
            model = gemini.GenerativeModel("gemini-1.5-flash")
            # print(prompt)
            response = model.generate_content(prompt)
            text = response.text
            print(text)
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
    def get_pplx_response(model_class: BaseModel, prompt: str, api_key: str, domain: str, disable_parse = None) -> str:
        """
        Get structured response from Perplexity API based on provided model class schema.
        
        Args:
            model_class: Pydantic BaseModel class defining the response schema
            prompt: Question/prompt to send to the API
            api_key: Perplexity API key
            
        Returns:
            str: JSON response string matching the model schema
        """
        url = "https://api.perplexity.ai/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "model": "sonar", 
            "messages": [
                {"role": "system", "content": "You are an AI agent that has access to the content from the web. You must respond only in the specific JSON format specified by the user and the content should be correct and accurate."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": model_class.model_json_schema()},
            },
            "search_domain_filter": [domain]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload).json()
            response_text = response["choices"][0]["message"]["content"].strip()
            ## cleaning the text

            if disable_parse == True:
                return response_text
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                result = response_text[start:end]
                return result.strip()
            else:
                raise ValueError("Model did not return a valid dictionary.")    
        except Exception as e:
            return f"Error getting response: {str(e)}"

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