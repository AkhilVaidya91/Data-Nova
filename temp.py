import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter
from typing import List

# Load environment variables
# load_dotenv()

def parse_pdf_with_directory_reader(pdf_path: str, parsing_instruction: str = None) -> List:
    """
    Parse PDF using SimpleDirectoryReader and LlamaParse
    
    Args:
        pdf_path (str): Path to the PDF file
        parsing_instruction (str, optional): Custom parsing instructions
    
    Returns:
        List: Parsed documents
    """
    print("Initializing LlamaParse for PDF parsing...")
    parser = LlamaParse(
        api_key="",
        result_type="markdown",
        parsing_instruction=parsing_instruction or "Extract text and maintain document structure"
    )
    
    print(f"Parsing PDF file: {pdf_path}")
    file_extractor = {".pdf": parser}
    documents = SimpleDirectoryReader(
        input_files=[pdf_path], 
        file_extractor=file_extractor
    ).load_data()
    
    print(f"Successfully parsed {len(documents)} documents from PDF.")
    return documents

def create_vector_store_index(documents: List, model_name: str = "BAAI/bge-small-en-v1.5") -> VectorStoreIndex:
    """
    Create a vector store index using Hugging Face embeddings
    
    Args:
        documents (List): List of documents to index
        model_name (str): Hugging Face embedding model name
    
    Returns:
        VectorStoreIndex: Indexed vector store
    """
    print("Initializing Hugging Face embedding model...")
    Settings.embed_model = HuggingFaceEmbedding(model_name=model_name)
    
    print("Setting up ingestion pipeline...")
    pipeline = IngestionPipeline(
        transformations=[
            # SentenceSplitter(chunk_size=50, chunk_overlap=5),
            # TitleExtractor(),
            TokenTextSplitter(
                chunk_size=2048,  # 2048 tokens per chunk
                chunk_overlap=200  # 200 tokens overlap between chunks
            ),
            Settings.embed_model  # Use the Hugging Face embedding model
        ]
    )
    
    print("Running ingestion pipeline...")
    nodes = pipeline.run(documents=documents)
    print(f"Successfully created {len(nodes)} vector nodes.")
    
    print("Creating vector store index...")
    index = VectorStoreIndex(nodes)
    print("Vector store index created successfully.")
    
    return index

def query_vector_store(index: VectorStoreIndex, query: str, top_k: int = 5):
    """
    Retrieve top k chunks from the vector store based on query
    
    Args:
        index (VectorStoreIndex): Indexed vector store
        query (str): User's query
        top_k (int): Number of top chunks to retrieve
    """
    print(f"\nQuerying vector store with: '{query}' (Top {top_k} results)...")
    retriever = index.as_retriever(similarity_top_k=top_k)
    retrieved_nodes = retriever.retrieve(query)
    
    print(f"\nTop {top_k} retrieved chunks:")
    for i, node in enumerate(retrieved_nodes, 1):
        print(f"\nChunk {i} (Score: {node.score}):")
        print(node.text)

def main():
    pdf_path = r"c:\Users\Akhil PC\Downloads\acc_repo.pdf"
    parsing_instruction = "Carefully extract all textual content, preserving formatting and structure"
    
    print("\nStarting PDF parsing process...")
    documents = parse_pdf_with_directory_reader(pdf_path, parsing_instruction)
    
    print("\nCreating vector store index...")
    index = create_vector_store_index(documents)
    
    query = "Extract the sections from this document report, that are related to the CSR or Corporate Social Responsibility or Sustainability."
    query_vector_store(index, query)
    
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    main()
