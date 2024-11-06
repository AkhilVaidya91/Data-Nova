import os
# from langchain_gemini import GeminiLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient

# Template remains unchanged
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "5. **Data only in table format:** Your output should contain only the the data specifically in the form of a table, with the relevant column names. Note that the table will later be used to convert to a dataframe, so do not add any extra information."
)

# gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini model with API key

def remove_comma(text):
    text = text.replace(",", "")
    return text

def parse_with_gemini(dom_chunks, parse_description, gemini_api_key):

    model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=gemini_api_key
    )
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response)
    parsed_results = parsed_results[0].content
    resp = remove_comma(parsed_results)

    return resp
