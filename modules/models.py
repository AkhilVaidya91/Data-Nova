from transformers import pipeline
import openai
import google.generativeai as gemini

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
                max_tokens=2000,
                temperature=0.2
            )
            # print(response.choices[0].message.content.strip())
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error calling OpenAI GPT-4o Mini: {e}"

    @staticmethod
    def call_gemini(prompt: str, api_key: str, disable_parse = None) -> str:
        """Call Google's Gemini model via Generative AI API."""
        gemini.configure(api_key=api_key)
        try:
            # print(prompt)
            model = gemini.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            # print(response)
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
            # return response.text
        except Exception as e:
            print(e)
            return f"Error calling Gemini model: {e}"

    @staticmethod
    def call_llama(prompt: str, api_key: str) -> str:
        """Call Llama 3.2 3B model using Hugging Face Transformers."""
        try:
            hf_pipeline = pipeline(
                "text-generation",
                model="meta-llama/Llama-3.2-3b",
                token=api_key
            )
            response = hf_pipeline(prompt, max_length=500, temperature=0.4)
            return response[0]['generated_text'].strip()
        except Exception as e:
            return f"Error calling Llama 3.2 3B: {e}"

    @staticmethod
    def call_mistral(prompt: str, api_key: str) -> str:
        """Call Mistral 7B model using Hugging Face Transformers."""
        try:
            hf_pipeline = pipeline(
                "text-generation",
                model="mistral/Mistral-7B",
                use_auth_token=api_key
            )
            response = hf_pipeline(prompt, max_length=500, temperature=0.4)
            return response[0]['generated_text'].strip()
        except Exception as e:
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


# Example usage:
# interface = LLMModelInterface()
# result = interface.call_openai_gpt4_mini(prompt="Hello, world!", api_key="your_openai_api_key")
# print(result)
