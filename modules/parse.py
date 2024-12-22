import os
from pymongo import MongoClient
import google.generativeai as genai
from openai import OpenAI
import json
import pandas as pd

def remove_comma(text):
    text = text.replace(",", "")
    return text

def parse_with_gemini(dom_chunks, parse_description, gemini_api_key):

    genai.configure(api_key = gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        prompt = (
        f"You are tasked with extracting specific information from the following text content: {chunk}. "
        "Please follow these instructions carefully: \n\n"
        f"1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
        "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
        "3. **Empty Response:** If no information matches the description, return an empty string ('')."
        "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
        "5. **Data only in table format:** Your output should contain only the the data specifically in the form of a markdown table, with the relevant column names. Note that the table will later be used to convert to a dataframe, so do not add any extra information at all, give ONLY THE TABLE OUTPUT."
        )
        response = model.generate_content(prompt)
        response = response.text.strip()
        parsed_results.append(response)

    parsed_results = parsed_results[0]
    resp = remove_comma(parsed_results)

    return resp

def clean_llm_json_response(json_str):
    # Remove any potential commentary before/after the JSON
    json_str = json_str.strip()
    start_idx = json_str.find('[')
    end_idx = json_str.rfind(']') + 1
    json_str = json_str[start_idx:end_idx]
    
    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON structure")
    
    # Validate data types and structure
    if not isinstance(data, list):
        raise ValueError("Output must be a JSON array")
    
    # Ensure all objects have the same keys
    if not data:
        raise ValueError("Empty data array")
    
    reference_keys = set(data[0].keys())
    for item in data:
        if set(item.keys()) != reference_keys:
            raise ValueError("Inconsistent keys across objects")
        
        # Validate data types
        for key, value in item.items():
            if not isinstance(value, (str, int)):
                raise ValueError(f"Invalid data type for key '{key}': {type(value)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

def parse_with_openai(dom_chunks, parse_description, openai_api_key):

    client = OpenAI(api_key=openai_api_key)
    prompt = """
You are a data structuring assistant. Your task is to convert the following unstructured text into a structured JSON array that can be directly converted into a pandas DataFrame.

Instructions:
1. Analyze the input text and identify key data fields.
2. Structure the data into a JSON array where each object has identical keys.
3. Follow these strict rules for data formatting:
   - Use only string or integer values (no nested objects or arrays)
   - For missing or unclear values, use "" for strings and -1 for numbers
   - Remove any special characters that could cause JSON parsing issues
   - Convert all dates to ISO format (YYYY-MM-DD)
   - Ensure consistent field names across all entries
   - Trim all string values
   - Convert any decimal numbers to integers by rounding

Expected output format:
[
    {
        "field1": "value1",
        "field2": 123,
        "field3": ""  // for missing string values
    },
    ...
]

Before responding:
- Ensure all objects in the array have the same keys
- Verify values are only strings or integers
- Check for consistent data types across each field
- Confirm there are no nested structures"""
    
    messages = [
        {
            "role": "system",
            "content": prompt
        },  
        {
            "role": "user",
            "content": dom_chunks
        },
    ]
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.1,
    )
    json_content = response.choices[0].message.content

    df = clean_llm_json_response(json_content)

    return df