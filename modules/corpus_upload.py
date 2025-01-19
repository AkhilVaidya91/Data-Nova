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

NUM_WORDS = 50 #characters

import json
from typing import Dict

def create_paper_analysis_prompt(paper_text: str) -> str:
    
    base_prompt = f"""You are a research paper analyzer specialized in extracting structured information using the TCM-ADO framework. Analyze the following research paper text and extract the requested information. Be precise and thorough in your analysis. If any information is not available in the text, return an empty string for that field.

Research Paper Text:
{paper_text}

Please extract and structure the following information in a precise JSON format:

1. Basic Information:
- Title: Extract the complete title of the paper
- Authors: List all authors
- Abstract: The complete abstract
- Keywords: Any keywords mentioned
- DOI: The Digital Object Identifier if present

2. TCM Analysis:
- Theories: Identify and summarize the main theoretical frameworks, concepts, or models used
- Contexts: Describe the research setting, conditions, or environments
- Methodologies: Detail the research methods, design, and analytical approaches used

3. ADO Analysis:
- Antecedents: Identify the factors, conditions, or situations that preceded or led to the main research focus
- Decisions: Extract the key choices, actions, or interventions discussed
- Outcomes: Summarize the main findings, results, or consequences

Format your response as a JSON object with these exact keys: "title", "authors", "abstract", "keywords", "doi", "theories", "contexts", "methodologies", "antecedents", "decisions", "outcomes"

Important guidelines:
- Maintain the exact key names as specified
- All values should be strings (if there are multiple values, do not make it a list object, instead use commas to separate them in a string only)
- Use empty strings ("") for any information not found in the text
- Ensure the JSON is properly formatted and valid, as a plain single level JSON and not any nested objects
- Be comprehensive in your extractions
- Do not include any explanatory text outside the JSON structure

Return only the JSON object with no additional text or explanations.The JSON structure should look like this (strictly follow this structure and ensure that you have all the keys mentioned in the given JSON structure):"""
    
    json_structure = (
    '{'
    '"title": "Title of the paper goes here",'
    '"authors": "Names of the authors comma separated",'
    '"abstract": "The exact abstract from the paper",'
    '"keywords": "comma separated keywords in the paper",'
    '"doi": "the exact matching DOI of the paper - note that this is a critical field as its the unique identifier, but if no DOI is found then give a blank string",'
    '"theories": "The core theories in this paper, if multiple then make them comma separated",'
    '"contexts": "The context behind the paper/study goes here",'
    '"methodologies": "Different types of methodologies that are used in the paper",'
    '"antecedents": "The antecedents mentioned or derived from the paper",'
    '"decisions": "The decisions mentioned or derived from the paper",'
    '"outcomes": "The outcomes mentioned or derived from the paper"'
    '}'
)
    
    base_prompt += json_structure

    return base_prompt

# def analyze_research_paper(paper_text: str, llm_function: callable) -> Dict[str, str]:
#     """
#     Analyzes a research paper using the TCM-ADO framework.
    
#     Args:
#         paper_text (str): The text content from the first page of a research paper
#         llm_function (callable): A function that takes a prompt and returns the LLM's response
        
#     Returns:
#         Dict[str, str]: A dictionary containing the structured analysis
#     """
    
#     # Generate the prompt
#     prompt = create_paper_analysis_prompt(paper_text)
    
#     # Get LLM response
#     response = llm_function(prompt)
    
#     try:
#         # Parse the JSON response
#         analysis = json.loads(response)
        
#         # Ensure all required keys are present
#         required_keys = {
#             "title", "authors", "abstract", "keywords", "doi",
#             "theories", "contexts", "methodologies",
#             "antecedents", "decisions", "outcomes"
#         }
        
#         # Add empty strings for any missing keys
#         for key in required_keys:
#             if key not in analysis:
#                 analysis[key] = ""
                
#         return analysis
    
    # except json.JSONDecodeError:
    #     raise ValueError("LLM response was not valid JSON")
    # except Exception as e:
    #     raise Exception(f"Error processing paper: {str(e)}")


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
            if st.button("Preprocess and Save Corpus"):


                

                file_contents = []
                total_files = len(extracted_text)
                progress_bar = st.progress(0)
                processed_count = 0

                for name, text in extracted_text.items():
                    # preprocessed = preprocess_text(text)
                    preprocessed = text

                    ## remove whitespace
                    preprocessed = preprocessed.replace("\n", " ")
                    preprocessed = preprocessed.replace("\t", " ")

                    while "  " in preprocessed:
                        preprocessed = preprocessed.replace("  ", " ")
                    preprocessed = preprocessed.strip()

                    ## split the text string into list of words
                    preprocessed = preprocessed.split(" ")

                    processed_data = []
                    for i in range(0, len(preprocessed), NUM_WORDS):
                        chunk = preprocessed[i:i+NUM_WORDS]
                        chunk = " ".join(chunk)
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
                    file_contents.append(file_content)

                    processed_count += 1
                    progress_bar.progress(int(processed_count / total_files * 100))

                corpus = {
                    "username": username,
                    "corpus_name": corpus_name,
                    "files": file_contents
                }
                st.json(corpus)

                # Save to MongoDB (placeholder for db_handler integration)
                # st.json(corpus)


                try:
                    # corpus_collection.insert_one(corpus)
                    st.success("Corpus processed and saved successfully.")
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                    
    
    with tab2:
        st.info("Upload a set of research paper PDFs for TCM-ADO Synthesis.")

        sysnthsis_name = st.text_input("Enter Synthesis Name")
        
        # 1. File upload section for multiple PDF files (research papers)
        research_files = st.file_uploader(
            "Upload Research PDF Files", 
            type=["pdf"], 
            accept_multiple_files=True
        )

        llm_model = st.selectbox("Select LLM Model", ["OpenAI", "Gemini", "Llama", "Mistral"])
        api_key_llm = st.text_input("Enter LLM API Key")

        if st.button("Analyze Research Papers"):
            extracted_texts = []
            dataframe_json_list = []
            # print(1)
            # 2. Parse each file, extracting text from the first page only
            for uploaded_pdf in research_files:
                try:
                    reader = PdfReader(uploaded_pdf)
                    if len(reader.pages) > 0:
                        first_page_text = reader.pages[0].extract_text()
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
                            "theories", "contexts", "methodologies",
                            "antecedents", "decisions", "outcomes"
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
