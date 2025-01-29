import PyPDF2
import re
import os
import pandas as pd
import statistics

def analyze_pdf_text(pdf_path):
    """
    Load a PDF file and analyze its text content with enhanced metrics.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing text statistics and ratios
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Basic counts
            full_stops = text.count('.')
            characters = len(''.join(text.split()))
            words = len(text.split())
            sentences = len(re.split(r'[.!?]+', text))
            
            # Calculate word lengths
            word_lengths = [len(word) for word in text.split()]
            
            # Advanced metrics
            avg_word_length = round(statistics.mean(word_lengths), 2) if word_lengths else 0
            median_word_length = round(statistics.median(word_lengths), 2) if word_lengths else 0
            
            # Ratios (multiplied by 100 for better readability)
            sentence_char_ratio = round((sentences / characters) * 100, 3) if characters else 0
            fullstop_char_ratio = round((full_stops / characters) * 100, 3) if characters else 0
            word_char_ratio = round((words / characters) * 100, 3) if characters else 0
            words_per_sentence = round(words / sentences, 2) if sentences else 0
            chars_per_sentence = round(characters / sentences, 2) if sentences else 0
            
            return {
                'full_stops': full_stops,
                'characters': characters,
                'words': words,
                'sentences': sentences,
                'avg_word_length': avg_word_length,
                'median_word_length': median_word_length,
                'sentence_char_ratio': sentence_char_ratio,
                'fullstop_char_ratio': fullstop_char_ratio,
                'word_char_ratio': word_char_ratio,
                'words_per_sentence': words_per_sentence,
                'chars_per_sentence': chars_per_sentence
            }
            
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
        return None
    except Exception as e:
        print(f"Error occurred with {pdf_path}: {str(e)}")
        return None

def analyze_directory(directory_path):
    """
    Analyze all PDF files in a directory and return results as a DataFrame.
    
    Args:
        directory_path (str): Path to the directory containing PDF files
        
    Returns:
        pandas.DataFrame: DataFrame containing analysis results for all PDFs
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist.")
        return None
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return None
    
    results = []
    
    for pdf_file in pdf_files:
        full_path = os.path.join(directory_path, pdf_file)
        stats = analyze_pdf_text(full_path)
        
        if stats:
            stats['filename'] = pdf_file
            results.append(stats)
    
    if results:
        df = pd.DataFrame(results)
        # Reorder columns to put filename first and group related metrics
        columns_order = [
            'filename',
            # Basic counts
            'characters', 'words', 'sentences', 'full_stops',
            # Word-level metrics
            'avg_word_length', 'median_word_length',
            # Ratios and advanced metrics
            'words_per_sentence', 'chars_per_sentence',
            'sentence_char_ratio', 'fullstop_char_ratio', 'word_char_ratio'
        ]
        df = df[columns_order]
        
        # Add summary row (only for numeric columns that make sense to sum)
        summary_cols = ['characters', 'words', 'sentences', 'full_stops']
        avg_cols = ['avg_word_length', 'median_word_length', 'words_per_sentence', 
                   'chars_per_sentence', 'sentence_char_ratio', 'fullstop_char_ratio', 
                   'word_char_ratio']
        
        summary = df[summary_cols].sum()
        averages = df[avg_cols].mean()
        
        summary_row = pd.Series(['TOTAL'], index=['filename'])
        summary_row = pd.concat([summary_row, summary])
        summary_row = pd.concat([summary_row, averages])
        
        df = pd.concat([df, summary_row.to_frame().T], ignore_index=True)
        
        return df
    
    return None

def print_analysis_results(df):
    """
    Print the analysis results in a formatted way with column descriptions.
    
    Args:
        df (pandas.DataFrame): DataFrame containing analysis results
    """
    if df is not None:
        print("\nPDF Analysis Results:")
        print("-" * 120)
        
        # Set display options for better formatting
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        
        print(df.to_string(index=False))
        print("-" * 120)
        
        # Print column descriptions
        print("\nColumn Descriptions:")
        descriptions = {
            'characters': 'Total number of characters (excluding whitespace)',
            'words': 'Total number of words',
            'sentences': 'Total number of sentences',
            'full_stops': 'Total number of periods/full stops',
            'avg_word_length': 'Average length of words',
            'median_word_length': 'Median length of words',
            'words_per_sentence': 'Average number of words per sentence',
            'chars_per_sentence': 'Average number of characters per sentence',
            'sentence_char_ratio': 'Sentences per 100 characters',
            'fullstop_char_ratio': 'Full stops per 100 characters',
            'word_char_ratio': 'Words per 100 characters'
        }
        
        for col, desc in descriptions.items():
            print(f"{col:20} : {desc}")

# Example usage
if __name__ == "__main__":
    directory_path = r"C:\Users\Akhil PC\Downloads\literature-review-temp"
    results_df = analyze_directory(directory_path)
    print_analysis_results(results_df)