# Standard library imports
import json
import logging
import re
from typing import Dict, Any, Iterator, KeysView,List, Tuple

# Third-party imports
import pandas as pd
import streamlit as st
from openai import OpenAI
import ast
import time

# Add this after your existing global constants but before class definitions






class DSIStructure:
    def __init__(self):
        self.themes: Dict[str, Dict[str, Any]] = {}
        self.features: Dict[str, Dict[str, Any]] = {}
        self.sub_features: Dict[str, Dict[str, Any]] = {}
    
    def items(self) -> Iterator[tuple[str, Dict[str, Any]]]:
        return self.themes.items()
    
    def keys(self) -> KeysView[str]:
        return self.themes.keys()



class DSITextProcessor:
    def __init__(self, logger):
        self.logger = logger
        
    def extract_social_elements(self, text: str) -> List[str]:
        # Should use SOCIAL_PATTERNS instead of redefining
        return self._extract_matches(text, SOCIAL_PATTERNS)

    def extract_digital_elements(self, text: str) -> List[str]:
        # Should use DIGITAL_PATTERNS instead of redefining
        return self._extract_matches(text, DIGITAL_PATTERNS)
    
    def extract_findings(self, text: str) -> List[str]:
        return self._extract_matches(text, FINDING_PATTERNS)
    
    def extract_theories(self, text: str) -> List[str]:
        return self._extract_matches(text, THEORY_PATTERNS)
    
    def extract_methods(self, text: str) -> List[str]:
        return self._extract_matches(text, METHOD_PATTERNS)
    
    def _extract_matches(self, text: str, patterns: List[str]) -> List[str]:
        matches = []
        text_lower = text.lower()
        
        # First check if sentence contains any methodology terms
        is_method_sentence = any(method in text_lower for method in METHOD_PATTERNS)
        
        # Only search for indicators if not a methodology sentence
        if not is_method_sentence:
            # Add fuzzy matching for variations
            for pattern in patterns:
                base_pattern = pattern.replace("-", "").replace(" ", "")
                
                # Check for exact match
                if pattern in text_lower:
                    sentence = self._get_sentence(text, text_lower.find(pattern))
                    matches.append(sentence.strip())
                    
                # Check for hyphenated variations
                hyphen_pattern = pattern.replace(" ", "-")
                if hyphen_pattern in text_lower:
                    sentence = self._get_sentence(text, text_lower.find(hyphen_pattern))
                    matches.append(sentence.strip())
                    
                # Check for compound variations 
                if base_pattern in text_lower.replace(" ", "").replace("-", ""):
                    pos = text_lower.replace(" ", "").replace("-", "").find(base_pattern)
                    sentence = self._get_sentence(text, pos)
                    matches.append(sentence.strip())
                        
        return list(set(matches))
    
  

    def _get_sentence(self, text: str, pos: int) -> str:
        start = text.rfind('.', 0, pos) + 1
        end = text.find('.', pos)
        if start == -1: start = 0
        if end == -1: end = len(text)
        return text[start:end].strip()


class DSIValidator:
    def __init__(self, logger):
        self.logger = logger

 
    def validate_match_strength(self, evidence: Dict[str, List[str]]) -> float:
   
        score = 0
        if evidence.get("Digital"):
            score += min(len(evidence["Digital"]) * EVIDENCE_WEIGHTS['digital'], EVIDENCE_WEIGHTS['digital'])
        if evidence.get("Social"):
            score += min(len(evidence["Social"]) * EVIDENCE_WEIGHTS['social'], EVIDENCE_WEIGHTS['social'])
        if evidence.get("Integration"):
            score += EVIDENCE_WEIGHTS['integration']
        return score

    


class AbstractAnalyzer:
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)
        self.dsi_structure = DSIStructure()
        self.logger = self._setup_logger()
        self.text_processor = DSITextProcessor(self.logger)
        self.validator = DSIValidator(self.logger)

    
    def analyze_abstract(self, abstract: str, abstract_number: int) -> Dict:
            """
            Main entry point for abstract analysis
            
            Args:
                abstract (str): Raw abstract text with TITLE, ABSTRACT, Keywords sections
                abstract_number (int): Unique identifier for the abstract
            
            Returns:
                Dict: Format:
                {
                    "T00": {
                        "Type": str,                # Research type
                        "Methods": str,             # Research methods
                        "Digital_Elements": str,     # Digital components found
                        "Social_Elements": str,      # Social aspects
                        "SDG_Alignments": str,      # All SDG alignments
                        "Key_Findings": str         # Main findings
                    },
                    "T01": {
                        "Match": str,              # Yes/No/Value
                        "Evidence": str            # Supporting evidence
                    },
                    ... # Additional theme matches
                }
            """
            try:
                return self.analyze_abstract_in_batches(abstract, abstract_number)
            except Exception as e:
                self.logger.error(f"Analysis failed for abstract {abstract_number}: {str(e)}")
                st.error(f"❌ Analysis failed for abstract {abstract_number}: {str(e)}")
                return self._create_error_response(str(e))

    def analyze_abstract_in_batches(self, abstract: str, abstract_number: int) -> Dict:
        """
        Process abstract in theme batches
        
        Args:
            abstract (str): Abstract text to analyze
            abstract_number (int): Abstract identifier
        
        Returns:
            Dict: Combined results from all batches
            {
                "T00": {...},    # Summary data
                "T01": {...},    # Theme 1 results
                "T02": {...},    # Theme 2 results
                ...
            }
        """
        all_responses = {}
        batch_ranges = [(1, 10)]
        max_retries = 3
        
        for start, end in batch_ranges:
            batch_successful = False
            retry_count = 0
            
            st.write(f"📢 Processing themes T{start:02d} to T{end:02d}")
            
            while not batch_successful and retry_count < max_retries:
                try:
                    prompt = self._create_analysis_prompt(abstract, start, end)
                    #st.write("GPT Prompt:",prompt)
                    raw_response = self._send_to_gpt(prompt)
                    
                    if not raw_response:
                        raise ValueError("Empty GPT response")
                    
                    #######
                    batch_results = self._safe_parse_response(raw_response, all_responses)
                    
                    st.write("batch results ", batch_results)
                    
                    if batch_results:
                        all_responses.update(batch_results)
                        batch_successful = True
                    else:
                        raise ValueError("Failed to parse batch results")
                        
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        self._handle_batch_error(start, end, all_responses)
                        break
                    time.sleep(2)
        
        return all_responses

    
    
    def _safe_parse_response(self, response_text: str, existing_themes: Dict = None) -> Dict:
        """
        Parse GPT response with consistent handling of SDGs and themes
        
        Args:
            response_text (str): Raw JSON from GPT
            existing_themes (Dict): Previously processed themes
        
        Returns:
            Dict: Standardized format with all SDGs and themes
        """
        existing_themes = existing_themes or {}
        
        try:
            parsed_data = json.loads(response_text)
            
            # Handle T00 summary section
            if "T00" in parsed_data and "T00" not in existing_themes:
                t00_data = parsed_data["T00"]
                
                # Improved methods cleaning while preserving rest of logic
                methods = t00_data.get("Methods", "")
                if isinstance(methods, str):
                    # Remove separator patterns
                    methods = methods.replace(" || ", " ")
                    methods = methods.replace("||", " ")
                    methods = methods.replace("|", "")
                    methods = methods.replace("  ", " ")
                    # Join split words
                    methods = "".join(methods.split())
                    # Add spaces before capitals for word separation
                    methods = ''.join([f" {c}" if c.isupper() and i > 0 else c 
                                     for i, c in enumerate(methods)])
                    # Clean up and split by common separators
                    methods = methods.strip()
                    method_list = []
                    for part in methods.split(","):
                        part = part.strip()
                        if part:
                            method_list.append(part)
                    methods = ", ".join(method_list) if method_list else methods
                
                # Create complete SDG alignments dictionary
                sdg_dict = {}
                for i in range(1, 18):
                    sdg_key = f"SDG{i:02d}"
                    sdg_dict[sdg_key] = {
                        "Match": "No",
                        "Evidence": "NA"
                    }
                
                # Update with matched SDGs from response
                sdg_alignments = t00_data.get("SDG_Alignments", [])
                for alignment in sdg_alignments:
                    if ":" in alignment:
                        sdg_num, evidence = alignment.split(":", 1)
                        sdg_num = sdg_num.strip()
                        if sdg_num in sdg_dict:
                            sdg_dict[sdg_num] = {
                                "Match": "Yes",
                                "Evidence": evidence.strip()
                            }
                
                # Format SDG output
                sdg_formatted = [
                    f"{sdg}: Match: {data['Match']}, Evidence: {data['Evidence']}"
                    for sdg, data in sdg_dict.items()
                ]

                existing_themes["T00"] = {
                    "Type": t00_data.get("Type", ""),
                    "Methods": methods,  # Cleaned methods string
                    "Digital_Elements": " || ".join(t00_data.get("Digital_Elements", [])),
                    "Social_Elements": " || ".join(t00_data.get("Social_Elements", [])),
                    "SDG_Alignments": sdg_dict,  # Store as dictionary
                    "Key_Findings": " || ".join(t00_data.get("Key_Findings", []))
                }
            
            # Handle all themes T01-T10
            for i in range(1, 11):
                theme_id = f"T{i:02d}"
                
                if theme_id in parsed_data:
                    theme_data = parsed_data[theme_id]
                    evidence = theme_data.get("Evidence", {})
                    
                    if theme_data.get("Match") == "Yes":
                        existing_themes[theme_id] = {
                            "Match": "Yes",
                            "Evidence": {
                                "Matched_Content": evidence.get("Matched_Content", []),
                                "Matched_Keywords": evidence.get("Matched_Keywords", [])
                            }
                        }
                    else:
                        existing_themes[theme_id] = {
                            "Match": "No",
                            "Evidence": {
                                "Matched_Content": [],
                                "Matched_Keywords": []
                            }
                        }
                else:
                    # Include missing themes with No match
                    existing_themes[theme_id] = {
                        "Match": "No", 
                        "Evidence": {
                            "Matched_Content": [],
                            "Matched_Keywords": []
                        }
                    }
            
            st.write("full display before return:", existing_themes)
            return existing_themes
                
        except Exception as e:
            self.logger.error(f"Response parsing error: {str(e)}")
            return existing_themes
        
        
    
    
    
    def _create_analysis_prompt(self, abstract: str, start_theme: int, end_theme: int) -> str:
        """Create analysis prompt"""
        # Parse abstract components
        lines = abstract.split('\n')
        title = next((line.replace('TITLE:', '').strip('[]').strip() 
                     for line in lines if line.startswith('TITLE:')), '')
        author_keywords = next((line.replace('Author Keywords:', '').strip('[]').split(';')
                              for line in lines if line.startswith('Author Keywords:')), [])
        index_keywords = next((line.replace('Index Keywords:', '').strip('[]').split(';')
                             for line in lines if line.startswith('Index Keywords:')), [])
        main_abstract = next((line.replace('ABSTRACT:', '').strip('[]').strip()
                            for line in lines if line.startswith('ABSTRACT:')), '')

        theme_descriptions = []
        for theme_id, theme in self.dsi_structure.themes.items():
            try:
                # Strip any text after numbers and convert to int
                theme_num = int(theme_id.replace('T', '').split()[0])
                if start_theme <= theme_num <= end_theme:
                    desc = theme['Description']
                    examples = theme.get('matching_examples', [])
                    
                    theme_desc = f"""
                    Theme {theme_id}:
                    Explanation: {desc['explanation']}
                    Pattern: {desc['pattern']}
                    Indicators: {desc['indicators']}
                    Keywords: {desc['keywords']}
                    Key Phrases: {desc['key_phrases']}
                    Examples: {'; '.join(examples)}
                    """
                    theme_descriptions.append(theme_desc)
            except ValueError:
                continue

        theme_descriptions_text = "\n".join(theme_descriptions)
        
        
        
    
        ##st.write(" IN ptompt theme decription: ", theme_descriptions_text)

        # Maintain original prompt format
        prompt = f'''Analyze this research paper's content for theme matching:

        PAPER CONTENT:
        Title: {title}
        Author Keywords: {'; '.join(author_keywords)}
        Index Keywords: {'; '.join(index_keywords)}
        Abstract: {abstract}

        DescriptionS TO MATCH:
        {theme_descriptions_text}

        ANALYSIS INSTRUCTIONS:
        0. symantic of matching abstract and abtract elements with Theme elemnts , use theme decription as guidelines if match is found tehn a single word or Yes/no should part theme match filed
        1. Extract key elements from abstract:
           - Research type and methods
           - Digital and social components
           - SDG alignments
           - Main findings

        2. Theme Matching with abstract Guidelines:
           - Use evidence directly from abstract or sbarecat elements text
           - Include relevant quotes from bastrcat elements 
           - Match keywords 
           - Map SDGs with specific numbers, with extracted sentenses as evidence 
           - Identify digital technologies (not analysis methods)
           - Find social innovation elements

        3. Evidence Requirements:
           - Direct quotes from abstract
           - Matching keywords
           - Clear connections to themes
           - semantic THEME MATCHing:
        4. Special Theme Values:
           - Research Type: Use exact type (Bibliometric/Literature/Case study/etc)
           - Methods: Use actual method names (co-citation/survey/etc)
           - All other themes: Use Yes/No

        5. Digital Elements Must Be:
           - Actual technologies
           - Digital platforms
           - Online systems
           - E-commerce/digital services
           - NOT data analysis methods or research techniques shoud clasified as digital elements 

        6 Mandatory Semantic similarity between abstract elements and Theme elements must be above 70% wherever is it YES and should have evendence of sentenses or keywords 
        
        7 SDG_Alignments must be above semantic similarity of above 70% between abstract element and SDG gaols 
       

        8 Do not Generate Theme results when there is NO Match
        
        OUTPUT FORMAT:
        {{
            "T00": {{
                "Type": "[Value: Bibliometric research/Literature review/Case study/Primary research/Secondary research/Editorial/Unknown,[co-word analisys =bibliometric]]",
                "Methods": "[Value: Actual methods used]",
                "Digital_Elements": [
                    "Only real digital/tech elements, not analysis methods"
                ],
                "Social_Elements": [
                    "Social aspects from text"
                ],
                "SDG_Alignments": [
                    "Format: SDG{{number}}: relevant content"
                ],
                "Key_Findings": [
                    "Main findings from abstract
                     past what we understand from this reserach aboout digital social innovation and SDGs
                     prsent what we understand from this reserach about digital social innovation and SDGs 
                     future what we see future from this resrach about digital social innovation and SDGs"
                ]
            }},
            
            "TXX"(xx is sr no of themes,generate for all themes): {{
                "Match": "[Yes/No or Value based on theme type]",
                "Evidence": {{
                    "Matched_Content": [
                        "Direct quotes from abstract"
                    ],
                    "Matched_Keywords": [
                        "Matching keywords found"
                    ]
                }}
            }}
        }}  
       
        
        
        
        
        
        Generate structured JSON response using exactly in above format.
        
    
        
        
        
        '''
        
        
        
        
        return prompt    
    
   

    def _send_to_gpt(self, prompt: str) -> str:
        """Send prompt to GPT API"""
        try:
            st.write("🔄 Sending request to GPT...")
            st.write("GPT prompt before sending " , prompt)
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return only a valid Python dictionary. No other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                timeout=45
            )
            raw_response = response.choices[0].message.content.strip()
            st.write("✅ Received GPT API response")
            st.write("Generated GPT API Result:", raw_response)
            return raw_response
        except Exception as e:
            self.logger.error(f"Error calling GPT API: {str(e)}")
            raise ValueError(f"GPT API Error: {str(e)}")

   
    
    
   
    
    
    
    
    

    
  
    
 

    def _handle_batch_error(self, start: int, end: int, all_responses: Dict) -> None:
        """Handle batch processing errors"""
        self.logger.error(f"\nHandling error for batch T{start:02d}-T{end:02d}")
        for theme_num in range(start, end + 1):
            theme_id = f"T{theme_num:02d}"
            if theme_id not in all_responses:
                default_result = self._create_default_theme_result()
                default_result["Justification"] = f"Batch processing error for themes T{start:02d}-T{end:02d}"
                all_responses[theme_id] = default_result

    def _create_default_theme_result(self) -> Dict:
        """Create default theme result structure"""
        return {
            "Match": "No",
            "Evidence": {
                "Matched_Content": [],
                "Matched_Keywords": []
            }
        }

    def _create_error_response(self, error_message: str = "Analysis error") -> Dict:
        """Create error response structure"""
        response = {"T00": self._create_default_summary()}
        response["T00"]["Type"] = f"Error: {error_message}"
        for i in range(1, 24):
            theme_id = f"T{i:02d}"
            response[theme_id] = self._create_default_theme_result()
        return response

    

    def _create_default_summary(self) -> Dict:
        """Create default summary structure"""
        return {
            "Type": "Unknown",
            "Methods": "",
            "Digital_Elements": [],
            "Social_Elements": [],
            "SDG_Alignments": [],
            "SDG_Summary": {
                "Past": "No Past interpretation available.",
                "Present": "No Present interpretation available.",
                "Future": "No Future interpretation available."
            },
            "Key_Findings": []
        }

        
    

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('AbstractAnalyzer')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        file_handler = logging.FileHandler('abstract_analysis.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    
 
    
    def load_dsi_master(self, file_df: str) -> None:
        """
        Load DSI master themes from Excel file
        """
        try:
            df = file_df
            
            # Expected columns
            expected_columns = [
                'ID', 
                'Description',
                'Examples'
            ]
            
            # Validate columns
            df.columns = [str(col).strip() for col in df.columns]
            missing_columns = [col for col in expected_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
            
            # Process each row
            for _, row in df.iterrows():
                id_str = str(row['ID']).strip()
                # id_str = row['ID'].strip()
                if not id_str or pd.isna(id_str):
                    continue
                    
                # Parse Description into components
                desc_text = str(row['Description'])
                description = {
                    # 'explanation': self._extract_component(desc_text, 'Explanation'),
                    'explanation': desc_text,
                    'pattern': self._extract_component(desc_text, 'Pattern'),
                    'indicators': self._extract_component(desc_text, 'Indicators'),
                    'keywords': self._extract_component(desc_text, 'Keywords'),
                    'key_phrases': self._extract_component(desc_text, 'Key Phrases')
                }
                
                # Store in DSI structure
                self.dsi_structure.themes[id_str] = {
                    'Description': description,
                    'matching_examples': str(row['Examples']).split(';')
                }    
                
            # st.write("shri zt")    
           
            self.logger.info(f"Successfully loaded {len(self.dsi_structure.themes)} themes")
            
        except Exception as e:
            self.logger.error(f"Failed to load DSI master: {str(e)}")
            raise

    def _extract_component(self, text: str, component: str) -> List[str]:
        """
        Extract component values from Description text
        """
        try:
            start = text.find(f"{component}:")
            if start == -1:
                return []
                
            end = text.find(":", start + len(component) + 1)
            if end == -1:
                end = len(text)
                
            value = text[start + len(component) + 1:end].strip()
            # Remove brackets and split on commas
            value = value.strip('[]')
            return [item.strip() for item in value.split(',') if item.strip()]
        except:
            return []





 