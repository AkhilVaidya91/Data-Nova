import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime
import time
from openai import OpenAI
import modules.excel_handler as eh
from modules.excel_handler import ExcelHandler
import modules.abstract_analyzer as abstract_analyzer
from modules.abstract_analyzer import AbstractAnalyzer
import tempfile
import shutil


class DSIAnalysisApp:
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.analyzer = None
        self.dsi_structure = None  # Initialize as None
    
    def save_uploaded_file(self, uploaded_file):
        """Save uploaded file and return path"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            return None

    def validate_api_key(self, api_key: str) -> bool:
        """Validate OpenAI API key"""
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            st.error(f"API Key validation failed: {str(e)}")
            return False

    
    ##################################
    def process_abstracts(self, df_abstracts: pd.DataFrame, model, hf_token) -> pd.DataFrame:
       """
       Process abstracts and generate analysis results with preserved column structure
       
       Args:
           df_abstracts (pd.DataFrame): Input DataFrame containing abstracts with columns:
               - AbstractID: Unique identifier
               - Abstract: Text content
               [Original columns preserved]
               
       Returns:
           pd.DataFrame: Results DataFrame with columns:
               [Original columns preserved]
               Added analysis columns:
               - Type: Research type classification
               - Methods: Research methods used
               - Digital Elements: Digital technologies identified
               - Social Elements: Social aspects identified  
               - Key Findings: Main findings extracted
               - SDG01-17 Match: SDG alignment (Yes/No)
               - SDG01-17 Evidence: Evidence for SDG alignment
               - T01-T10 Match: Theme matches (Yes/No) 
               - T01-T10 Evidence: Evidence for theme matches
       """
       # Store original columns to preserve
       original_columns = df_abstracts.columns.tolist()
       
       # Define analysis result columns
       analysis_columns = [
           "Type", "Methods", "Digital Elements", "Social Elements", 
           "Key Findings"
       ]
       
       # Define SDG columns (01-17)
       sdg_columns = []
       for i in range(1, 18):
           sdg_columns.extend([
               f"SDG{i:02d} Match",
               f"SDG{i:02d} Evidence"
           ])
           
       # Define Theme columns (T01-T10) 
       theme_columns = []
       for i in range(1, 11):
           theme_columns.extend([
               f"T{i:02d} Match",
               f"T{i:02d} Evidence"
           ])
       
       # Initialize results list
       results_list = []
       
       # Process each abstract
       for idx in range(len(df_abstracts)):
           if pd.notna(df_abstracts.iloc[idx]['Combined']):
               try:
                   # Get analysis results
                #    print(model, hf_token)
                   results = self.analyzer.analyze_abstract(
                       str(df_abstracts.iloc[idx]['Combined']),
                       abstract_number=idx + 1, 
                       model_type = model, 
                       hf_token = hf_token
                   )
                   
                   # Initialize result row with original data
                   result_row = df_abstracts.iloc[idx].to_dict()
                   
                   # Add analysis results
                   result_row.update({
                       "Type": results.get("T00", {}).get("Type", "NA"),
                       "Methods": results.get("T00", {}).get("Methods", "NA"),
                       "Digital Elements": results.get("T00", {}).get("Digital_Elements", "NA"),
                       "Social Elements": results.get("T00", {}).get("Social_Elements", "NA"),
                       "Key Findings": results.get("T00", {}).get("Key_Findings", "NA")
                   })

                   # Add SDG results
                   sdg_alignments = results.get("T00", {}).get("SDG_Alignments", {})
                   for i in range(1, 18):
                       sdg_code = f"SDG{i:02d}"
                       sdg_data = sdg_alignments.get(sdg_code, {"Match": "No", "Evidence": "NA"})
                       result_row[f"{sdg_code} Match"] = sdg_data["Match"]
                       result_row[f"{sdg_code} Evidence"] = sdg_data["Evidence"]

                   # Add Theme results
                   for i in range(1, 11):
                       theme_id = f"T{i:02d}"
                       theme_data = results.get(theme_id, {})
                       result_row[f"{theme_id} Match"] = theme_data.get("Match", "No")
                       evidence = theme_data.get("Evidence", {})
                       content = evidence.get("Matched_Content", [])
                       result_row[f"{theme_id} Evidence"] = " || ".join(content) if content else "NA"

                   results_list.append(result_row)

               except Exception as e:
                   print(f"Error processing abstract {idx + 1}: {e}")
                   # Preserve original data on error
                   error_row = df_abstracts.iloc[idx].to_dict()
                   error_row.update({col: "NA" for col in analysis_columns + sdg_columns + theme_columns})
                   error_row["Type"] = f"Error: {str(e)}"
                   results_list.append(error_row)

       # Create DataFrame with all columns
       df_results = pd.DataFrame(results_list)
       
       # Ensure all expected columns exist
       all_columns = original_columns + analysis_columns + sdg_columns + theme_columns
       for col in all_columns:
           if col not in df_results.columns:
               df_results[col] = "NA"
       
       # Order columns correctly
       df_results = df_results[all_columns]
       
       return df_results



    
    
    
    
    
    
    
   
    
    
    

    
   
   
  
    
    def save_and_download_results(self, df_results):
        """Save results and create download button"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"analyzed_abstracts_{timestamp}.xlsx"
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, output_filename)
            
            # Debug print
            print(f"Saving file to temp directory: {output_path}")
            
            # Save Excel file
            self.excel_handler.save_excel(df_results, output_path)
            
            # Create download button
            with open(output_path, 'rb') as f:
                file_data = f.read()
                st.download_button(
                    label="📥 Download Analysis Results",
                    data=file_data,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"✅ Analysis complete! Click above to download results.")
            st.write("Preview of analysis results:")
            st.dataframe(df_results.head())
            
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp directory: {e}")
                
            return output_filename
                
        except Exception as e:
            st.error(f"Error saving results: {str(e)}")
            return None
    

    def run(self, dsi_master_df, abstracts_file, op_api_key, model, hf_token):
        # st.title("DSI Research Abstract Analysis Tool")

        # dsi_master_file = st.file_uploader("Upload DSImaster.xlsx", type=['xlsx'])
        
        # Get OpenAI API Key
        # api_key = st.text_input("Enter OpenAI API Key:", type="password")
        if not op_api_key:
            st.warning("Please enter your OpenAI API Key to proceed")
            return
            
        # Here's where the code should go - replace the existing if dsi_master_file block
        if dsi_master_df is not None:
            try:
                if self.validate_api_key(op_api_key):
                    self.analyzer = AbstractAnalyzer(op_api_key)
                    # dsi_master_path = self.save_uploaded_file(dsi_master_file)
                    if dsi_master_df is not None:
                        self.analyzer.load_dsi_master(dsi_master_df)
                        self.dsi_structure = self.analyzer.dsi_structure  # Add this line
                        # print(self.dsi_structure)  # Debug print
                        # st.success("DSI master file loaded successfully")
                        # os.remove(dsi_master_path)  # Clean up
                    else:
                        st.error("Failed to save DSI master file")
                        return
                else:
                    return
            except Exception as e:
                st.error(f"Error initializing analyzer: {str(e)}")
                return
        
        
        if True:
            try:
                # df_abstracts = pd.read_excel(abstracts_file)
                df_abstracts = abstracts_file
                
                if 'Combined' not in df_abstracts.columns:
                    st.error("Input file must contain an 'Combined' column")
                    st.write("Available columns:", list(df_abstracts.columns))
                    return
                
                # st.write("Preview of abstracts to analyze:")
                # st.dataframe(df_abstracts[['Combined']].head())
                
                if st.button("Start Analysis"):
                    try:
                        # Process abstracts
                        # print(model, hf_token)
                        df_results = self.process_abstracts(df_abstracts, model, hf_token)
                        
                        # Save and download results
                        output_file = self.save_and_download_results(df_results)
                        
                        # Cleanup
                        if output_file and os.path.exists(output_file):
                            os.remove(output_file)
                            
                    except Exception as e:
                        st.error(f"Error during analysis process: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading abstracts file: {str(e)}")
                st.info("Please ensure your file is a valid Excel file with an 'Abstract' column")
                


def main(dsi_master_df, abstracts_file, op_api_key, model, hf_token = None):
    app = DSIAnalysisApp()
    # print(op_api_key)
    app.run(dsi_master_df, abstracts_file, op_api_key, model, hf_token)
    # (df, df_abstracts, openai_key, model, huggingface_key)