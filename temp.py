import os
import streamlit as st
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.ingestion import IngestionPipeline
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Set page configuration
st.set_page_config(page_title="PDF Processing Pipeline", layout="wide")

# Load environment variables
# load_dotenv()

# def parse_pdf_with_directory_reader(pdf_path: str, parsing_instruction: str = None) -> List:
#     """
#     Parse PDF using SimpleDirectoryReader and LlamaParse
    
#     Args:
#         pdf_path (str): Path to the PDF file
#         parsing_instruction (str, optional): Custom parsing instructions
    
#     Returns:
#         List: Parsed documents
#     """
#     with st.spinner(f"Parsing PDF: {os.path.basename(pdf_path)}..."):
#         parser = LlamaParse(
#             api_key=st.session_state.api_key,
#             # result_type="markdown",
#             fast_mode=True,
#             parsing_instruction=parsing_instruction or "Carefully extract all textual content, preserving formatting, preferably write everython in a single column document structure and ensure that all the individual sentences end with a period (full-stop)."
#         )
        
#         file_extractor = {".pdf": parser}
#         documents = SimpleDirectoryReader(
#             input_files=[pdf_path], 
#             file_extractor=file_extractor
#         ).load_data()
        
#         st.info(f"Successfully parsed {len(documents)} documents from {os.path.basename(pdf_path)}")
#         return documents

def parse_pdf_with_directory_reader(pdf_path: str, parsing_instruction: str = None) -> List:
    """
    Parse PDF directly using SimpleDirectoryReader
    
    Args:
        pdf_path (str): Path to the PDF file
        parsing_instruction (str, optional): Custom parsing instructions (not used with direct reading)
    
    Returns:
        List: Parsed documents
    """
    with st.spinner(f"Parsing PDF: {os.path.basename(pdf_path)}..."):
        # Use SimpleDirectoryReader with default PDF extractor instead of LlamaParse
        documents = SimpleDirectoryReader(
            input_files=[pdf_path]
        ).load_data()
        
        st.info(f"Successfully parsed {len(documents)} documents from {os.path.basename(pdf_path)}")
        return documents

def create_vector_store_index(documents: List, model_name: str) -> VectorStoreIndex:
    """
    Create a vector store index using Hugging Face embeddings
    
    Args:
        documents (List): List of documents to index
        model_name (str): Hugging Face embedding model name
    
    Returns:
        VectorStoreIndex: Indexed vector store
    """
    with st.spinner("Creating vector store index..."):
        Settings.embed_model = HuggingFaceEmbedding(model_name=model_name)
        
        pipeline = IngestionPipeline(
            transformations=[
                TokenTextSplitter(
                    chunk_size=st.session_state.chunk_size,
                    chunk_overlap=st.session_state.chunk_overlap
                ),
                Settings.embed_model
            ]
        )
        
        nodes = pipeline.run(documents=documents)
        st.info(f"Created {len(nodes)} vector nodes")
        
        index = VectorStoreIndex(nodes)
        return index

def query_vector_store(index: VectorStoreIndex, query: str, top_k: int = 7):
    """
    Retrieve top k chunks from the vector store based on query
    
    Args:
        index (VectorStoreIndex): Indexed vector store
        query (str): User's query
        top_k (int): Number of top chunks to retrieve
        
    Returns:
        List: Retrieved nodes
    """
    with st.spinner(f"Querying vector store..."):
        retriever = index.as_retriever(similarity_top_k=top_k)
        retrieved_nodes = retriever.retrieve(query)
        return retrieved_nodes

def save_results_to_file(retrieved_nodes, output_path):
    """
    Save retrieved nodes to a PDF file
    
    Args:
        retrieved_nodes: Retrieved nodes from vector store
        output_path (str): Path to save the output file
    """
    # Change extension from .txt to .pdf
    output_path = output_path.replace('.txt', '.pdf')
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title = Paragraph(f"Top {len(retrieved_nodes)} retrieved chunks:", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add each chunk with its score
    for i, node in enumerate(retrieved_nodes, 1):
        # Add chunk header
        chunk_header = Paragraph(f"Chunk {i} (Score: {node.score}):", styles['Heading2'])
        story.append(chunk_header)
        story.append(Spacer(1, 6))
        
        # Add chunk text
        chunk_text = Paragraph(node.text, styles['Normal'])
        story.append(chunk_text)
        story.append(Spacer(1, 12))
        
        # Add separator
        separator = Paragraph("-" * 80, styles['Normal'])
        story.append(separator)
        story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)

def process_pdf(pdf_path, output_dir, parsing_instruction, query, model_name, top_k):
    """
    Process a single PDF and save results
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save output
        parsing_instruction (str): Custom parsing instructions
        query (str): Query to search for
        model_name (str): Embedding model name
        top_k (int): Number of top chunks to retrieve
        
    Returns:
        bool: Success status
    """
    try:
        # Create output filename based on input PDF name
        pdf_filename = os.path.basename(pdf_path)
        output_filename = os.path.splitext(pdf_filename)[0] + ".pdf"  # Changed to .pdf
        output_path = os.path.join(output_dir, output_filename)
        
        # Rest of the function remains the same
        documents = parse_pdf_with_directory_reader(pdf_path, parsing_instruction)
        index = create_vector_store_index(documents, model_name)
        retrieved_nodes = query_vector_store(index, query, top_k)
        save_results_to_file(retrieved_nodes, output_path)
        
        return True
    except Exception as e:
        st.error(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")
        return False
    

def main():
    st.title("PDF Processing Pipeline")
    
    # Initialize session state for settings
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'chunk_size' not in st.session_state:
        st.session_state.chunk_size = 2048
    if 'chunk_overlap' not in st.session_state:
        st.session_state.chunk_overlap = 200
    
    # Create sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # LlamaParse API Key
        st.session_state.api_key = st.text_input(
            "LlamaParse API Key", 
            value=st.session_state.api_key,
            type="password"
        )
        
        # Embedding model selection
        model_name = st.selectbox(
            "Embedding Model",
            ["BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5", "BAAI/bge-large-en-v1.5"],
            index=0
        )
        
        # Chunking parameters
        st.session_state.chunk_size = st.number_input(
            "Chunk Size (tokens)",
            min_value=256,
            max_value=4096,
            value=st.session_state.chunk_size
        )
        
        st.session_state.chunk_overlap = st.number_input(
            "Chunk Overlap (tokens)",
            min_value=0,
            max_value=1000,
            value=st.session_state.chunk_overlap
        )
        
        # Top-k parameter
        top_k = st.number_input(
            "Top-K Results",
            min_value=1,
            max_value=20,
            value=7
        )
    
    # Main area for file upload and processing
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    # Parse instruction and query
    parsing_instruction = st.text_area(
        "PDF Parsing Instruction",
        value="Carefully extract all textual content, preserving formatting, preferably write everython in a single column document structure and ensure that all the individual sentences (note sentences, not words or simple headings) end with a period (full-stop)."
    )
    
    query = st.text_area(
        "Query for Vector Search",
        value="Extract the sections from this document report, that are related to the CSR or Corporate Social Responsibility or Sustainability."
    )
    
    # Output directory
    output_dir = st.text_input(
        "Output Directory",
        value="output"
    )
    
    if st.button("Process PDFs"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file")
            return
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            st.info(f"Created output directory: {output_dir}")
        
        # Process each PDF
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_count = 0
        for i, uploaded_file in enumerate(uploaded_files):
            # Save uploaded file temporarily
            temp_file_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Update status
            status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            # Process PDF
            success = process_pdf(
                temp_file_path,
                output_dir,
                parsing_instruction,
                query,
                model_name,
                top_k
            )
            
            if success:
                successful_count += 1
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Clean up temp file
            os.remove(temp_file_path)
        
        # Final status update
        st.success(f"Successfully processed {successful_count}/{len(uploaded_files)} PDF files")
        st.info(f"Results saved to {output_dir} directory")
        
        # Clean up temp directory
        if os.path.exists("temp"):
            os.rmdir("temp")

if __name__ == "__main__":
    main()