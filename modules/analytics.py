import streamlit as st
import pandas as pd
import os
import json
from pymongo import MongoClient
from modules.utils import cosine_similarity
from modules.models import LLMModelInterface

MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
THRESHOLD_SCORE = 0.3

PROMPT = ''

client = MongoClient(MONGO_URI)
db = client['digital_nova']
corpus_collection = db['corpus']
theme_collection = db['themes']
analytics_collection = db['analytics']
corpus_file_content = db["corpus_file_content"]

def generate_prompt_template(SDG_DESC, FILE_TEXT):
    prompt = (
        "You are an expert auditor tasked with critically analyzing the annual reports of various companies to validate their alignment with the United Nations Sustainable Development Goals (UN SDGs). "
        "I will provide you with excerpts from these reports, and your task is to evaluate whether the projects, initiatives, or actions mentioned in the excerpts align with any of the 17 UN SDGs.\n\n"
        "Ensure that the alignment is clear, direct and strong enough for the initiatives to be considered valid and acceptable under the specified goals.\n\n"
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
        "- **Evidence**: Provide the exact matching text **statement** from the excerpt (10–15 words) **only about a project, action, or initiative** if \"Yes\". Note that the statement should only be from the report's excerpt and not from the original description of the SDGs (don't confuse between the two).\n\n"
        "**Important Notes:**\n"
        "- Note that when you are considering a particular initiative as an activity under a particular SDG, it should explicitly align with the given SDG and not just sound like one, this is a strict and hard constraint to be followed ensuring that a project is considered as an SDG aligned activity if and only if it perfectly aligns with the SDG. This is an important step to prevent LLM hallucination, don't fill in the gaps, respond only if the information is directly provided."
        "- Your response must always include all 17 SDGs, even if the presence is \"No\" for any or all.\n"
        "- The response should be directly parsable as a JSON, with all elements (keys and values) enclosed in double quotes.\n"
        "- Do not include any text outside the JSON format, such as explanations or backticks, not even the word json.\n\n"
        "Please respond in the JSON structure specified."
    )
    return prompt

def generate_synthesis_template(text_list):
    prompt = (
        "You are an expert researcher specializing in semantic clustering of concepts. You are provided with a large text corpus from a table, where each row contains a DOI or identifier as the key and a concept or theme as the value. Apart from these core titles, there will be a few additional properties such as number of citations etc. Your task is to:\n\n"
        "1. **Analyze** all themes in the provided text input.\n"
        "2. **Identify** n major clusters of semantically similar themes. Note that there should be atleast 3-4 clusters in this corpus.\n"
        "3. **Assign** each theme to the most appropriate cluster.\n"
        "4. **Return** the identifiers (DOIs or keys) associated with each cluster in a structured format. Ensure that you are returning the exact same DOI IDs as mentined in the input text as it is a unique identifier.\n\n"
        "Note that for each cluster, you have to assign at most 10 DOIs and not more. These top 10 DOIs should be selected based on their additional properties such as number of citations, jornal quality, recency of the publication etc.\n\n"
        "Your response should be in **JSON format only**, with no additional explanation or text. Do not even write the word json or backticks in your response. Ensure that your exact output JSON string is directly parasable into a python dictionary. The structure should be as follows:\n\n"
        "{\n"
        "\"Cluster 1 Title\": [\"ID or DOI 1\", \"ID or DOI 2\", \"ID or DOI 3\", ... (string of the  exact input IDs)],\n"
        "\"Cluster 2 Title\": [\"ID or DOI 1\", \"ID or DOI 2\", \"ID or DOI 3\", ... (string of the  exact input IDs)],\n"
        "...\n"
        "\"Cluster n Title\": [\"ID or DOI 1\", \"ID or DOI 2\", \"ID or DOI 3\", ... (string of the  exact input IDs)]\n"
        "}\n\n"
        "Each \"Cluster Description\" should summarize the theme of the cluster in a few words. The corresponding array should contain all identifiers that belong to that cluster."
        f"Here is the input text:\n\n"
        f"{text_list}"
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
    st.info("RAG Based LLM Analytics and Synthesis")

    tab1, tab2, tab3 = st.tabs(["Analytics", "Synthesis", "Quantative Analytics"])

    with tab1:

    ## dropdowns for themes and corpus

        theme_names = theme_collection.distinct("theme_name")
        corpus_names = corpus_collection.distinct("corpus_name")

        theme_choice = st.selectbox("Select Theme", theme_names)
        corpus_choice = st.selectbox("Select Corpus", corpus_names)

        ## fetching the theme and corpus data
        if theme_choice and st.button("Analyze"):

            theme_data = theme_collection.find_one({"theme_name": theme_choice})
            corpus_data = corpus_collection.find_one({"corpus_name": corpus_choice})

            files_ids = corpus_data["files"]    ## list of dictionaries
            files = []
            for file_id in files_ids:
                file_doc = corpus_file_content.find_one({"_id": file_id})
                if file_doc:
                    files.append(file_doc)
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
                match_counts = {}
                
                for i, ref_vector_dict in enumerate(ref_vectors, 1):
                    ref_text = ref_vector_dict["text"]
                    ref_vector = ref_vector_dict["vector"]
                    match_count = 0

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
                    top_3_texts = [text for text, similarity in similarities[:10]]
                    matched_texts = [text for text, similarity in similarities if similarity >= THRESHOLD_SCORE]
                    match_counts[f"Ref_Vector_{i}_Matches"] = len(matched_texts)

                    ## drop elements if the score is less than THRESHOLD_SCORE

                    top_k_texts = [text for text in top_3_texts if similarity >= 0.2]
                    # top_k_texts = [text for text in top_3_texts if True]

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
                flat_dict.update(match_counts)
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

    with tab2:

        ## upload an Excel file with multiple columns

        st.info("Upload an Excel file with TCM-ADO columns to generate a synthesis report. Ensure that your input excel has TCM-ADO columns.")

        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

        if uploaded_file:
            df = pd.read_excel(uploaded_file)  ## reading the uploaded file
            column_names = df.columns.tolist()

            selected_columns = st.multiselect("Select columns for synthesis", column_names)

            if st.button("Generate Synthesis"):
                batch_size = 50  # Define the batch size
                total_rows = len(df)
                # print(total_rows)
                result_list = []
                # flat_dict = {}
                keys = []
                values = []
                
                # df = pd.DataFrame(columns=["Cluster Title", "DOIs"])
                prompt_template = ""
                for start in range(0, total_rows, batch_size):
                    end = min(start + batch_size, total_rows)
                    batch_df = df.iloc[start:end]
                    
                    text_list = []
                    for _, row in batch_df.iterrows():
                        text = ""
                        for column in selected_columns:
                            text += f"{column} : {str(row[column])} | "

                        text_list.append(text.strip())
                    
                    combined_text = "\n\n".join(text_list)
                    prompt_template = generate_synthesis_template(combined_text)
                    st.text(f"Processing batch {start // batch_size + 1}: Prompt length {len(prompt_template)}")

                    # st.text(prompt_template)
                    llm_interface = LLMModelInterface()
                    if model == "OpenAI":
                        response = llm_interface.call_openai_gpt4_mini(prompt_template, api_key)
                    elif model == "Gemini":
                        # st.text(prompt_template)
                        response = llm_interface.call_gemini(prompt_template, api_key)
                        # response = ''
                    elif model == "Llama":
                        response = llm_interface.call_llama(prompt_template, api_key)
                    elif model == "Mistral":
                        # print("Mistral")
                        response = llm_interface.call_mistral(prompt_template, api_key)
                        # print(response)
                    else:
                        st.error("Unsupported model selected.")
                        break
                    
                    text = response.strip()
                    
                    if "{" in text and "}" in text:
                        start_brace = text.find("{")
                        end_brace = text.rfind("}") + 1
                        json_str = text[start_brace:end_brace]
                        response = json_str.strip()
                    
                    if response:
                        
                        try:
                            parsed_json = json.loads(response)
                            

                            for dict_key, dict_value in parsed_json.items():
                                keys.append(dict_key)
                                values.append(dict_value)
                        except json.JSONDecodeError as e:
                            st.error(f"JSON decode error in batch {start // batch_size + 1}: {e}")
                    else:
                        st.warning(f"No response received for batch {start // batch_size + 1}.")
                
                if len(keys) > 0 and len(values) > 0:

                    res = {
                        "Cluster Title": keys,
                        "DOIs": values
                    }


                    result_df = pd.DataFrame(res)
                    result_df = replace_null_values(result_df)  # Ensure no null values
                    st.dataframe(result_df)
                    
                    # Store the analytics dataframe on MongoDB
                    analytics_collection.insert_one({
                        "username": username,
                        "theme": theme_choice,
                        "corpus": corpus_choice,
                        "result": result_df.to_dict(orient="records")
                    })
                    
                    st.success("Analytics generated successfully!")
                    
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Analytics as CSV",
                        data=csv,
                        file_name=f"{theme_choice}_{corpus_choice}_analytics.csv",
                        mime='text/csv',
                    )
                else:
                    st.warning("No analytics data was generated.")
    with tab3:
        pass