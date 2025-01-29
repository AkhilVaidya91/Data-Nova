import streamlit as st
import os
from pymongo import MongoClient
from PyPDF2 import PdfReader
from modules.utils import preprocess_text
from modules.models import LLMModelInterface
import pandas as pd
llm_interface = LLMModelInterface()
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
corpus_collection = db['corpus']
synthesis_collection = db['synthesis']
corpus_file_content = db["corpus_file_content"]
themes_collection = db['themes']

NUM_WORDS = 50 #characters

import json
from typing import Dict
from sklearn.metrics.pairwise import cosine_similarity

import re

def split_into_sentences(text):

    # Common abbreviations to ignore
    abbreviations = {
        'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'etc', 'vs',
        'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        'dept', 'univ', 'est', 'approx', 'inc', 'co', 'ltd'
    }
    
    # First, protect periods in known abbreviations
    for abbr in abbreviations:
        # Replace period after abbreviations with a special marker
        pattern = r'\b' + abbr + r'\.'
        text = re.sub(pattern, abbr + '@@@', text, flags=re.IGNORECASE)
    
    # Protect decimal numbers
    text = re.sub(r'(\d+)\.(\d+)', r'\1@@@\2', text)
    
    # Protect ellipsis
    text = text.replace('...', '@@@')
    
    # Protect initials
    text = re.sub(r'\b([A-Z])\.\s*([A-Z])\.\s*', r'\1@@@ \2@@@ ', text)
    
    # Split on sentence endings followed by spaces and capital letters
    sentences = re.split(r'[.!?]+\s+(?=[A-Z])', text)
    
    # Clean up sentences
    cleaned_sentences = []
    for sentence in sentences:
        # Restore protected periods
        sentence = sentence.replace('@@@', '.')
        # Remove extra whitespace
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        if sentence:  # Only add non-empty sentences
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

def create_paper_analysis_prompt(paper_text: str) -> str:

    base_prompt = f"""
You are a research paper analyzer specializing in extracting structured information using the TCCM-ADO framework. Your task is to extract precise, evidence-supported information from the following research paper text. Strictly adhere to the guidelines provided to ensure clarity, consistency, and minimal hallucinations.

### Research Paper Text:
{paper_text}

### Framework Definitions and Guidelines:

1. **Basic Information:**
   - **Title**: Extract the full and exact title of the paper without modifying or summarizing it.
   - **Authors**: List all authors as they appear in the paper, separated by commas.
   - **Abstract**: Extract the complete abstract exactly as it appears in the paper.
   - **Keywords**: Extract all mentioned keywords, separated by commas. If none are explicitly mentioned, return an empty string.
   - **DOI**: Provide the exact Digital Object Identifier (DOI). If no DOI is available, return an empty string.
   - **Paper Type**: Identify the type of paper (e.g., empirical, literature, methodology, survey, interview based, editorial, etc.)

2. **TCCM Analysis:**
   - **Theories**: 
     - Identify and summarize the main theoretical frameworks, models, or paradigms explicitly mentioned in the paper (e.g., Social Cognitive Theory, Diffusion of Innovation).
     - Theories must have direct evidence from the paper, provided in a separate key (`theories_evidence`).
   - **Contexts**: 
     - Describe the setting, environment, or conditions in which the research was conducted (e.g., "rural healthcare centers in India," "urban schools in the USA").
     - Contexts must have direct evidence from the paper, provided in a separate key (`contexts_evidence`).
   - **Concepts**:
     - List the core concepts, variables, or constructs the paper explores (e.g., "employee engagement," "renewable energy adoption").
     - Concepts must be explicitly stated in the paper and evidence should be traceable.
   - **Methodologies**:
     - Extract the research methods, design, and analytical approaches used (e.g., "survey-based study," "regression analysis," "randomized controlled trial", or whatever mentioned in the paper content).
     - Note that Methodologies and Theories are distinct components, dont mix them up.
     - Methodologies must have direct evidence, provided in a separate key (`methodologies_evidence`).

3. **ADO Analysis:**
   - **Antecedents**:
     - Identify factors, conditions, or situations that precede or lead to the research focus (e.g., "increased demand for sustainable energy solutions").
     - Provide direct evidence from the paper for each antecedent in a separate key (`antecedents_evidence`).
   - **Decisions**:
     - Extract key choices, actions, or interventions made or discussed in the paper (e.g., "implementation of machine learning algorithms").
     - Provide evidence sentences from the paper for each decision in a separate key (`decisions_evidence`).
   - **Outcomes**:
     - Summarize the main findings, results, or consequences of the research (e.g., "reduction in energy consumption by 20%").
     - Outcomes must have supporting evidence from the paper, provided in a separate key (`outcomes_evidence`).

### Important Guidelines:
- **Key Structure**: 
  Maintain the exact keys specified. Use empty strings ("") for fields where information is not found.
- **Evidence Requirements**: 
  Every field in the TCCM-ADO analysis must include an accompanying evidence key containing direct, verbatim sentences from the paper. Do not infer or assume information. Re-check if the TCCM-ADO fields do actually match clearly with the evidence provided.
- **Respond with the TCM columns if and only if the paper has any on ground research or surveys of actual reports.**
- **String Format**:
  All values should be formatted as strings. If there are multiple values, combine them into a single string separated by commas.
- **JSON Format**:
  The output must be a valid, plain JSON object with no nested structures. Ensure proper formatting and include all required keys, even if the values are empty strings.
- **No Explanatory Text**:
  Return only the JSON object. Do not include any additional text, explanations, or commentary outside the JSON.

### Example Output:
Here is the exact structure to follow:
{{
    "title": "The full title of the paper",
    "authors": "Names of the authors",
    "abstract": "The complete abstract text",
    "keywords": "keyword1, keyword2, keyword3",
    "doi": "DOI or an empty string if not available",
    "paper_type": "Type of the paper",
    "theories": "Theory1, Theory2",
    "theories_evidence": "Direct evidence sentences supporting the theories",
    "contexts": "Context description",
    "contexts_evidence": "Direct evidence sentences supporting the contexts",
    "concepts": "Concept1, Concept2",
    "methodologies": "Methodology1, Methodology2",
    "methodologies_evidence": "Direct evidence sentences supporting the methodologies",
    "antecedents": "Antecedent1, Antecedent2",
    "antecedents_evidence": "Direct evidence sentences supporting the antecedents",
    "decisions": "Decision1, Decision2",
    "decisions_evidence": "Direct evidence sentences supporting the decisions",
    "outcomes": "Outcome1, Outcome2",
    "outcomes_evidence": "Direct evidence sentences supporting the outcomes"
}}

Analyze the provided research paper and return your response in this strict JSON format:
"""

    json_structure = """
{
    "title": "",
    "authors": "",
    "abstract": "",
    "keywords": "",
    "doi": "",
    "paper_type": "",
    "theories": "",
    "theories_evidence": "",
    "contexts": "",
    "contexts_evidence": "",
    "concepts": "",
    "methodologies": "",
    "methodologies_evidence": "",
    "antecedents": "",
    "antecedents_evidence": "",
    "decisions": "",
    "decisions_evidence": "",
    "outcomes": "",
    "outcomes_evidence": ""
}
"""
    
    base_prompt += json_structure
    return base_prompt


def corpus_page(username, model, api_key):
    """Page to handle corpus upload and preprocessing."""
    st.subheader("PDF Corpus Upload")

    tab1, tab2 = st.tabs(["Corpus Upload", "Structured LIterature Synthesis"])

    with tab1:

        st.info("Upload a set of PDF documents for analysis.")

        # Corpus name input
        corpus_name = st.text_input("Enter Corpus Name")

        # File uploader
        uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

        if uploaded_files and corpus_name:
            

            st.write("Processing uploaded files...")
            extracted_text = {}
            
            for file in uploaded_files:
                try:
                    reader = PdfReader(file)
                    text = " ".join(page.extract_text() for page in reader.pages)
                    extracted_text[file.name] = text
                except Exception as e:
                    st.warning(f"Failed to process {file.name}: {e}")

            # Display summary
            st.write("Extraction Summary:")
            st.json({name: len(text) for name, text in extracted_text.items()})

            # Preprocess and vectorize
            print(2)
            if st.button("Preprocess and Save Corpus"):
                print(1)
                file_contents = []
                total_files = len(extracted_text)
                progress_bar = st.progress(0)
                processed_count = 0
                file_ids = []
                for name, text in extracted_text.items():
                    # preprocessed = preprocess_text(text)
                    preprocessed = text
                    sentences = split_into_sentences(preprocessed)
                    # ## remove whitespace
                    # preprocessed = preprocessed.replace("\n", " ")
                    # preprocessed = preprocessed.replace("\t", " ")

                    # while "  " in preprocessed:
                    #     preprocessed = preprocessed.replace("  ", " ")
                    # preprocessed = preprocessed.strip()

                    # ## split the text string into list of words
                    # preprocessed = preprocessed.split(" ")

                    processed_data = []
                    # for i in range(0, len(preprocessed), NUM_WORDS):
                    for sentence in sentences:
                        # chunk = preprocessed[i:i+NUM_WORDS]
                        # chunk = " ".join(chunk)
                        chunk = sentence
                        if model == "OpenAI":
                            vector = llm_interface.embed_openai(chunk, api_key)
                            # pass
                        elif model == "Gemini":
                            vector = llm_interface.embed_gemini(chunk, api_key)

                        elif model == "USE":
                            vector = llm_interface.embed_use(chunk)

                        elif model == "MiniLM - distilBERT":
                            vector = llm_interface.embed_distilBERT(chunk)

                        processed_data.append({"text": chunk, "vector": vector})

                    file_content = {
                        "filename": name,
                        "processed_data": processed_data,
                        "model": model
                    }
                    inserted_doc = corpus_file_content.insert_one(file_content)
                    file_ids.append(inserted_doc.inserted_id)
                    # file_contents.append(file_content)

                    processed_count += 1
                    progress_bar.progress(int(processed_count / total_files * 100))

                corpus_doc = {
                    "username": username,
                    "corpus_name": corpus_name,
                    "files": file_ids
                }
                # st.json(corpus)

                try:
                    corpus_collection.insert_one(corpus_doc)
                    st.success("Corpus processed and saved successfully.")
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                    
    
    with tab2:
        st.info("Upload a set of research paper PDFs for TCCM-ADO Synthesis.")

        sysnthsis_name = st.text_input("Enter Synthesis Name")
        
        theme_names = themes_collection.distinct("theme_name")
        theme_choice = st.selectbox("Select Theme", theme_names)
        

        # 1. File upload section for multiple PDF files (research papers)
        research_files = st.file_uploader(
            "Upload Research PDF Files", 
            type=["pdf"], 
            accept_multiple_files=True
        )

        llm_model = st.selectbox("Select LLM Model", ["OpenAI", "Gemini", "Llama", "Mistral"])
        api_key_llm = st.text_input("Enter LLM API Key")

        if st.button("Analyze Research Papers"):
            theme_data = themes_collection.find_one({"theme_name": theme_choice})
            ref_vectors = theme_data["reference_vectors"]
            # for ref_vector_dict in ref_vectors:
            #     ref_text = ref_vector_dict["text"]
            #     ref_vector = ref_vector_dict["vector"]

            extracted_texts = []
            dataframe_json_list = []
            # print(1)
            # 2. Parse each file, extracting text from the first page only
            for uploaded_pdf in research_files:
                try:
                    reader = PdfReader(uploaded_pdf)
                    if len(reader.pages) > 0:
                        first_page_text = reader.pages[0].extract_text()
                        second_page_text = reader.pages[1].extract_text()
                        third_page_text = reader.pages[2].extract_text()
                        # remaining_text = ""

                        # for page_index in range(3, len(reader.pages)):
                        #     text_part = reader.pages[page_index].extract_text()
                        #     if text_part:
                        #         remaining_text += text_part

                        # all_chunks = []
                        # chunk_size = 1000
                        # for i in range(0, len(remaining_text), chunk_size):
                        #     chunk_text = remaining_text[i : i + chunk_size]

                        #     # Vectorize each chunk
                        #     if model == "OpenAI":
                        #         chunk_vector = llm_interface.embed_openai(chunk_text, api_key_llm)
                        #     elif model == "Gemini":
                        #         chunk_vector = llm_interface.embed_gemini(chunk_text, api_key_llm)
                        #     elif model == "USE":
                        #         chunk_vector = llm_interface.embed_use(chunk_text)
                        #     elif model == "MiniLM - distilBERT":
                        #         chunk_vector = llm_interface.embed_distilBERT(chunk_text)
                        #     else:
                        #         chunk_vector = []

                        #     all_chunks.append({"text": chunk_text, "vector": chunk_vector})

                        # # For each reference vector, find the top-1 matching chunk and append its text
                        # for ref_vec_dict in ref_vectors:
                        #     ref_vector = ref_vec_dict["vector"]
                        #     best_similarity = float("-inf")
                        #     best_chunk_text = ""
                        #     for chunk in all_chunks:
                        #         sim = cosine_similarity([chunk["vector"]], [ref_vector])
                        #         if sim > best_similarity:
                        #             best_similarity = sim
                        #             best_chunk_text = chunk["text"]
                        #     if best_chunk_text:
                        #         first_page_text += f"\n\n{best_chunk_text}"

                        # extracted_texts.append(
                        #     {
                        #         "filename": uploaded_pdf.name,
                        #         "first_page_plus_matches": first_page_text.strip()
                        #     }
                        # )



                        ## chunk and vectorize the remaining page text

                        ## identify the top 1 match with respect to each of the reference vectors

                        ## append the top 1 matches to the first page text

                        if len(reader.pages) > 5:
                            fourth_page_text = reader.pages[3].extract_text()
                            # fifth_page_text = reader.pages[4].extract_text()
                            first_page_text = first_page_text + second_page_text + third_page_text + fourth_page_text
                        else:
                            first_page_text = first_page_text + second_page_text + third_page_text
                        first_page_text = first_page_text.replace("\n", " ")
                        first_page_text = first_page_text.replace("\t", " ")
                        while "  " in first_page_text:
                            first_page_text = first_page_text.replace("  ", " ")
                        extracted_texts.append(first_page_text.strip())
                except Exception as e:
                    st.error(f"Error processing {uploaded_pdf.name}: {e}")

            for text_content in extracted_texts:
                prompt = create_paper_analysis_prompt(text_content)
                response = ""

                if llm_model == "OpenAI":
                    response = llm_interface.call_openai_gpt4_mini(prompt, api_key_llm)
                elif llm_model == "Gemini":
                    # st.text(prompt)
                    response = llm_interface.call_gemini(prompt, api_key_llm)
                elif llm_model == "Llama":
                    response = llm_interface.call_llama(prompt, api_key_llm)
                elif llm_model == "Mistral":
                    # st.text(prompt)
                    response = llm_interface.call_mistral(prompt, api_key_llm)

                text = response.strip()
                
                if "{" in text and "}" in text:
                    start_brace = text.find("{")
                    end_brace = text.rfind("}") + 1
                    json_str = text[start_brace:end_brace]
                    response = json_str.strip()
                
                if response:
                    
                    try:
                        parsed_json = json.loads(response)

                        # Ensure all required keys are present

                        required_keys = {
                            "title", "authors", "abstract", "keywords", "doi",
                            "theories", "theories_evidence", "contexts",  "contexts_evidence", "methodologies", "methodologies_evidence",
                            "antecedents", "antecedents_evidence", "decisions", "decisions_evidence", "outcomes", "outcomes_evidence"
                        }

                        # Add empty strings for any missing keys

                        for key in required_keys:
                            if key not in parsed_json:
                                parsed_json[key] = ""

                        # st.json(parsed_json)
                        dataframe_json_list.append(parsed_json)
            
                    except json.JSONDecodeError:
                        st.error("LLM response was not valid JSON")
                    except Exception as e:
                        st.error(f"Error processing paper: {str(e)}")

            df = pd.DataFrame(dataframe_json_list)

            # print(df)
            if dataframe_json_list:
                monog_insert = {
                    "username": username,
                    "synthesis_name": sysnthsis_name,
                    "structured_data": dataframe_json_list
                }

                ## storing on MongoDB in the synthesis collection

                try:
                    
                    synthesis_collection.insert_one(monog_insert)
                    st.dataframe(df)
                    st.success("Research Papers analyzed and saved successfully.")
                except Exception as e:
                    st.error(f"Error saving analysis: {e}")
            else:
                st.warning("No data to save.")
