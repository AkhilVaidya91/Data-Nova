import os
import logging
import pandas as pd
from typing import Dict, List


class ExcelHandler:
    def __init__(self):
        self.df = None
        self.logger = self._setup_logger()  # Add logging
        
    
    def read_excel(self, file_path: str) -> pd.DataFrame:
        """Read Excel file with validation"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")
                
            self.df = pd.read_excel(file_path)
            
            if not self._validate_dataframe(self.df):  # Use validation method
                raise ValueError("Excel file is empty or invalid")
                
            return self.df
            
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {str(e)}")
            raise
    
   
    
    def add_analysis_columns(self, df: pd.DataFrame, analysis_results: Dict[str, Dict[str, any]]) -> pd.DataFrame:
        """Add analysis results as new columns with validation"""
        if df is None or df.empty:
            raise ValueError("Input DataFrame is None or empty")
        if not self._validate_dataframe(df):
            raise ValueError("Input DataFrame is None or empty")
        if not analysis_results:
            raise ValueError("Analysis results dictionary is empty")

        try:
            # First add Summary if present
            if "Summary" in analysis_results:
                summary_data = analysis_results["Summary"]
                # Add summary columns
                df["Research_Type"] = summary_data.get("Type", "")
                df["Digital_Elements"] = [';'.join(str(e) for e in elements) if elements else "" 
                                        for elements in summary_data.get("Digital_Elements", [])]
                df["Social_Elements"] = [';'.join(str(e) for e in elements) if elements else ""
                                       for elements in summary_data.get("Social_Elements", [])]
                df["Key_Points"] = [';'.join(str(p) for p in points) if points else ""
                                  for points in summary_data.get("Key_Points", [])]

                # Add extracted elements if present
                if "Extracted_Elements" in summary_data:
                    extracted = summary_data["Extracted_Elements"]
                    df["Digital_Found"] = [';'.join(str(d) for d in extracted.get("Digital", []))]
                    df["Social_Found"] = [';'.join(str(s) for s in extracted.get("Social", []))]
                    df["Methods_Found"] = [';'.join(str(m) for m in extracted.get("Methods", []))]
                    df["Findings_Found"] = [';'.join(str(f) for f in extracted.get("Findings", []))]

            # Process all themes T01.00 to T23.00
            theme_ids = [f"T{str(i).zfill(2)}.00" for i in range(1, 24)]
            for theme_id in theme_ids:
                theme_data = analysis_results.get(theme_id, {})
                
                # Add basic theme results
                df[f"{theme_id}_Match"] = theme_data.get("Match", "No")
                df[f"{theme_id}_Match_Strength"] = theme_data.get("Match_Strength", "0%")
                df[f"{theme_id}_Justification"] = theme_data.get("Justification", "")
                
                # Add evidence if present
                evidence = theme_data.get("Evidence", {})
                if evidence:
                    df[f"{theme_id}_Digital_Evidence"] = [';'.join(str(d) for d in evidence.get("Digital", []))]
                    df[f"{theme_id}_Social_Evidence"] = [';'.join(str(s) for s in evidence.get("Social", []))]
                    df[f"{theme_id}_Integration"] = evidence.get("Integration", "")
                    df[f"{theme_id}_Methods"] = [';'.join(str(m) for m in evidence.get("Methods", []))]
                    df[f"{theme_id}_Findings"] = [';'.join(str(f) for f in evidence.get("Findings", []))]
                
                # Add features and sub-features
                df[f"{theme_id}_Features"] = ';'.join(str(f) for f in theme_data.get("Features", []))
                df[f"{theme_id}_Sub-features"] = ';'.join(str(sf) for sf in theme_data.get("Sub-features", []))

            return df

        except Exception as e:
            self.logger.error(f"Error adding analysis columns: {str(e)}")
            raise ValueError(f"Error adding analysis columns: {str(e)}")
        
    
    
    
    
    def save_excel(self, df: pd.DataFrame, output_path: str):
        """Save DataFrame to Excel with error handling"""
        try:
            if df is None or df.empty:
                raise ValueError("No data to save")
                
            # Check write permissions
            output_dir = os.path.dirname(output_path)
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"No write permission for {output_dir}")
                
            df.to_excel(output_path, index=False)
            self.logger.info(f"Successfully saved Excel file to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving Excel file: {str(e)}")
            raise
    
   
     
     # Helper/private methods last (with underscore prefix)
    
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('ExcelHandler')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _validate_dataframe(self, df: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """Validate DataFrame structure"""
        if df is None or df.empty:
            return False
            
        if required_columns and not all(col in df.columns for col in required_columns):
            return False
            
        return True