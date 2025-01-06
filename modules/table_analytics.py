import pandas as pd
import json
import openai
from modules.models import LLMModelInterface

llm_interface = LLMModelInterface()

def combine_columns(data_df, selected_columns):
    data_df['Combined'] = data_df[selected_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return data_df

# Function to generate structured explanation template from themes_df
def generate_theme_explanations(themes_df, selected_columns):
    explanations = []
    for i, row in themes_df.iterrows():
        explanation = f"T{i+1}:\n"
        for col in selected_columns:
            explanation += f"{col}: {row[col]}\n"
        explanations.append(explanation.strip())
    return explanations

def generate_prompt_template():
    template = (
        "You are an AI model tasked with extracting theme-based structured data from a given text. "
        "You will be given a text that has been extracted from maybe a few reports or research papers, and a detailed description of the n number of themes. "
        "For each theme provided, identify its presence in the text and extract a direct/indirect evidence string.\n"
        "Note that the text can also be associated or matched with multiple themes not necessarily one. "
        "Respond only in JSON format. The JSON structure should look like this:\n\n"
        "{\n"
        "  \"T01\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  },\n"
        "  \"T02\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  },\n"
        "  ...\n"
        "  \"Txx\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  }\n"
        "}\n\n"
        "If Presence is \"No\", set Evidence to an empty string."
        "Ensure that your response always has all the T01 to Txx themes (keys), even if the presence is \"No\" for all."
        "If there are n number of themes (T1 - Tn) mentioned in the given text, THERE SHOULD ALWAYS BE n NUMBER OF KEYS IN THE in the JSON response.\n\n"
        "Generate structured JSON response using exactly in above format. Give only the JSON and no other text at all, not even the word json or backtics. The response text should be directly parsable as a Python dictionary. DO NOT INCLUDE ANY OTHER TEXT IN THE RESPONSE."
    )
    return template

# Function to call GPT-4 and process the response
# def call_openai_gpt4_mini(prompt: str, api_key: str) -> str:
#     """Call OpenAI's GPT-4o Mini model."""
#     client = openai.OpenAI(api_key = api_key)
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#             {"role": "developer", "content": "You are an instruction following AI model that behaves and strictly follows the instructions given to you in the prompt."},
#             {"role": "user", "content": prompt}
#         ],
#             max_tokens=2000,
#             temperature=0.1
#         )
#         # print(response.choices[0].message.content.strip())
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error calling OpenAI GPT-4o Mini: {e}"

# Function to process all rows in data_df and create the final dataframe
def process_data(data_df, theme_explanations, prompt_template, API_KEY, model):
    result_list = []

    for idx, row in data_df.iterrows():
        combined_text = row['Combined']
        explanations = theme_explanations
        # print(theme_explanations)
        
        prompt = f"{prompt_template}\n\nText:\n{combined_text}\n\nThemes:\n{str(explanations)}"

        if model == "GPT-4o":
            response = llm_interface.call_openai_gpt4_mini(prompt, API_KEY)
        elif model == "Gemini":
            response = llm_interface.call_gemini(prompt, API_KEY, disable_parse=True)
        elif model == "Llama":
            response = llm_interface.call_llama(prompt, API_KEY)
        elif model == "Mistral":
            response = llm_interface.call_mistral(prompt, API_KEY)
        

        # response = call_openai_gpt4_mini(prompt, API_KEY)
        text = response.strip()

        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            result = text[start:end]
            response = result.strip()
        
        if response:
            try:
                # Parse the returned JSON
                parsed_json = json.loads(response)
                # Flatten the JSON structure
                flat_dict = {}
                for theme_key, theme_value in parsed_json.items():
                    if isinstance(theme_value, dict):
                        for sub_key, sub_value in theme_value.items():
                            new_key = f"{theme_key} {sub_key}"  # e.g., "T01 Presence"
                            flat_dict[new_key] = sub_value
                    else:
                        # If there's a top-level key that isn't a dict
                        flat_dict[theme_key] = theme_value

                result_list.append(flat_dict)
            except Exception as e:
                print(f"Skipping row {idx} due to JSON parse error: {e}")
        else:
            print(f"Skipping row {idx} due to error.")

    # Convert results to dataframe
    result_df = pd.DataFrame(result_list)
    return result_df

# Main function to orchestrate the workflow
def table_analytics_main(themes_df, data_df, theme_columns, data_columns, API_KEY, model):
    # Step 1: Combine selected columns in data_df
    data_df = combine_columns(data_df, data_columns)

    # Step 2: Generate structured theme explanations
    theme_explanations = generate_theme_explanations(themes_df, theme_columns)

    # Step 3: Generate the prompt template
    prompt_template = generate_prompt_template()

    # Step 4: Process each row and get the final dataframe
    final_df = process_data(data_df, theme_explanations, prompt_template, API_KEY, model)

    return final_df