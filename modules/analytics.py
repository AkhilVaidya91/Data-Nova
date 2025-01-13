import streamlit as st
import pandas as pd
import os
import json
from pymongo import MongoClient
from modules.utils import cosine_similarity
from modules.models import LLMModelInterface

MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
THRESHOLD_SCORE = 0.1

client = MongoClient(MONGO_URI)
db = client['digital_nova']
corpus_collection = db['corpus']
theme_collection = db['themes']
analytics_collection = db['analytics']

def generate_prompt_template(SDG_DESC, FILE_TEXT):
    prompt = (
        "You are an expert auditor tasked with critically analyzing the annual reports of various educational institutes to validate their alignment with the United Nations Sustainable Development Goals (UN SDGs). "
        "I will provide you with excerpts from these reports, and your task is to evaluate whether the projects, initiatives, or actions mentioned in the excerpts align with any of the 17 UN SDGs.\n\n"
        "Ensure that the alignment is strong enough for the initiatives to be considered valid and acceptable under the specified goals.\n\n"
        "### UN SDGs Overview\n"
        "Each SDG has keywords and example projects that may be considered under its domain. The examples are indicative, not exhaustive.\n\n"
        f"{SDG_DESC}\n\n"
        "### Excerpts from the reports:\n\n"
        f"{FILE_TEXT}\n\n"
        "### Response Format\n"
        "You must always respond in JSON format, using the following structure:\n\n"
        "{\n"
        "  \"SDG-1\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  },\n"
        "  \"SDG-2\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  },\n"
        "  ...\n"
        "  \"SDG-17\": {\n"
        "    \"Presence\": \"Yes\" or \"No\",\n"
        "    \"Evidence\": \"string\"\n"
        "  }\n"
        "}\n\n"
        "- **Presence**: Indicate \"Yes\" if the initiative aligns with the respective SDG, otherwise \"No\".\n"
        "- **Evidence**: Provide the exact matching text from the excerpt (in short) if \"Yes\". If \"No\", leave this field as an empty string.\n\n"
        "**Important Notes:**\n"
        "- Your response must always include all 17 SDGs, even if the presence is \"No\" for any or all.\n"
        "- The response should be directly parsable as a Python dictionary.\n"
        "- Do not include any text outside the JSON format, such as explanations or backticks, not even the word json.\n\n"
        "Please respond in the JSON structure specified."
    )
    return prompt

def replace_null_values(df):
    for column in df.columns:
        if "Presence" in column:
            df[column].fillna("No", inplace=True)
        elif "Evidence" in column:
            df[column].fillna("", inplace=True)
    return df

def analytics_page(username, model, api_key):
    st.subheader("Analytics")
    st.info("RAG Based LLM analytics")

    ## dropdowns for themes and corpus

    theme_names = theme_collection.distinct("theme_name")
    corpus_names = corpus_collection.distinct("corpus_name")

    theme_choice = st.selectbox("Select Theme", theme_names)
    corpus_choice = st.selectbox("Select Corpus", corpus_names)

    ## fetching the theme and corpus data
    if theme_choice and st.button("Analyze"):

        theme_data = theme_collection.find_one({"theme_name": theme_choice})
        corpus_data = corpus_collection.find_one({"corpus_name": corpus_choice})

        files = corpus_data["files"]    ## list of dictionaries
        ref_vectors = theme_data["reference_vectors"] ## list of dictionaries
        result_list = []
        for file in files:
            # print(1)
            file_name = file["filename"]
            # print(file_name)
            data = file["processed_data"] ## list of dictionaries with text and vector keys
            data = [(d["text"], d["vector"]) for d in data]

            similar_texts = []  ## list of lists of strings
            ref_text_string = ""    ## UN SDG description text
            
            for ref_vector in ref_vectors:
                ref_text = ref_vector["text"]
                ref_vector = ref_vector["vector"]

                ## calculating cosine similarity
                similarities = []
                for text, vector in data:
                    if len(vector) != len(ref_vector):
                        st.warning("Please ensure that the embedding dimensions are the same.")
                        return
                    similarity = cosine_similarity(ref_vector, vector)
                    similarities.append((text, similarity))

                ## sorting the similarities
                similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
                top_3_texts = [text for text, similarity in similarities[:3]]

                ## drop elements if the score is less than THRESHOLD_SCORE

                top_k_texts = [text for text in top_3_texts if similarity >= THRESHOLD_SCORE]

                similar_texts.extend(top_k_texts)

                ref_text_string += ref_text + "\n\n"

            context_reference = "\n\n\n".join(similar_texts) ## --> this is the texts extracted from the file

            prompt_template = generate_prompt_template(ref_text_string, context_reference)

            # st.text(prompt_template)

            llm_interface = LLMModelInterface()

            if model == "OpenAI":
                response = llm_interface.call_openai_gpt4_mini(prompt_template, api_key)
            elif model == "Gemini":
                response = llm_interface.call_gemini(prompt_template, api_key)
            elif model == "Llama":
                response = llm_interface.call_llama(prompt_template, api_key)
            elif model == "Mistral":
                response = llm_interface.call_mistral(prompt_template, api_key)

            text = response.strip()

            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                result = text[start:end]
                response = result.strip()
            
            if response:
                flat_dict = {}
                try:
                    parsed_json = json.loads(response)
                    
                    for theme_key, theme_value in parsed_json.items():
                        if isinstance(theme_value, dict):
                            for sub_key, sub_value in theme_value.items():
                                new_key = f"{theme_key} {sub_key}"  # e.g., "SDG-1 Presence"
                                flat_dict[new_key] = sub_value
                        else:
                            # If there's a top-level key that isn't a dict
                            flat_dict[theme_key] = theme_value

                    
                except Exception as e:
                    print(f"Skipping file {file_name} due to JSON parse error: {e}")
                    ## adding a blank dictionary to the result_list
                    # result_list.append({})
            result_list.append(flat_dict)
            # else:
            #     print(f"Skipping file {file_name} due to error.")

        result_df = pd.DataFrame(result_list)

        ## replacing null values with "No" and empty string - No if Presence word is in the column title and empty string if Evidence word is in the column title

        # result_df = replace_null_values(result_df)

        filenames = [file["filename"] for file in files]
        filename_df = pd.DataFrame(filenames, columns=["File Name"])

        result_df = pd.concat([filename_df, result_df], axis=1)

        st.dataframe(result_df)

        ## store the analytics dataframe on mongodb

        analytics_collection.insert_one({
            "username": username,
            "theme": theme_choice,
            "corpus": corpus_choice,
            "result": result_df.to_dict(orient="records")
        })

        st.success("Analytics generated successfully!")

        # st.download_button(
        #     label="Download as Excel",
        #     data=result_df.to_excel,
        #     file_name=f"{theme_choice}_{corpus_choice}.xlsx",
        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )