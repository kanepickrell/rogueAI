import os
import shutil
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores.chroma import Chroma  
import logging
from typing import Dict, List, Optional
from collections import defaultdict
import re
from docling.document_converter import DocumentConverter
from langchain.schema import Document

def clean_directory(directory: str) -> None:
    """Safely clean a directory and its contents"""
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)

def convert_with_docling(pdf_path: str) -> dict:
    """Convert PDF using Docling with minimal features"""
    try:
        # Configure converter to only use essential features
        converter = DocumentConverter(
            config={
                "ocr": False,  # Disable OCR since we don't need it
                "pipeline": {
                    "layout_analysis": True,
                    "table_recognition": True,
                    "metadata_extraction": False,  # Disable if not needed
                    "language_detection": False,
                },
                "runtime": {
                    "max_threads": 4,  # Limit thread usage
                    "batch_size": 1  # Process one page at a time
                }
            }
        )
        result = converter.convert(pdf_path)
        return result.document.export_to_json()
    except Exception as e:
        logging.error(f"Docling conversion failed: {str(e)}")
        return None

def extract_tables_from_docling(docling_output: dict) -> List[dict]:
    """Extract tables from Docling JSON output"""
    tables = []
    if docling_output and 'pages' in docling_output:
        for page in docling_output['pages']:
            for element in page.get('elements', []):
                if element.get('type') == 'table':
                    tables.append({
                        'page': page['page_number'],
                        'content': element,
                        'structure': element.get('structure', {}),
                        'headers': element.get('headers', [])
                    })
    return tables

def create_vector_store(pdf_path: str, persist_directory: str):
    """
    Create a local vector store from a PDF document using Chroma DB.
    Now enhanced with Docling table processing.
    """
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        logger.info(f"Cleaning existing directory at {persist_directory}")
        clean_directory(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)

        # Process with Docling first
        logger.info("Processing document with Docling")
        docling_output = convert_with_docling(pdf_path)
        tables = extract_tables_from_docling(docling_output)
        
        # Load PDF with LangChain
        logger.info(f"Loading PDF from {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Create special chunks for tables
        table_documents = []
        for table in tables:
            table_doc = Document(
                page_content=str(table['content']),
                metadata={
                    'page': table['page'],
                    'type': 'table',
                    'source': pdf_path,
                    'headers': table['headers']
                }
            )
            table_documents.append(table_doc)

        # Split regular content
        logger.info("Splitting text into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=200,
            separators=[
                "\nTable",          # Keep tables together
                "\n\nA\.",          # Major sections
                "\n\n\d+\.",        # Numbered sections
                "\n\n",             # Paragraphs
                "\n",               
                ". ",               
                " ",                
            ]
        )

        regular_chunks = text_splitter.split_documents(documents)
        
        # Combine regular chunks with table documents
        all_documents = regular_chunks + table_documents

        logger.info("Initializing embedding model")
        embedding_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )

        logger.info("Creating vector store")
        vectordb = Chroma.from_documents(
            documents=all_documents,
            embedding=embedding_model,
            persist_directory=persist_directory
        )
        
        logger.info(f"Vector store created and persisted to {persist_directory}")
        return vectordb

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        try:
            clean_directory(persist_directory)
        except:
            pass
        raise

def verify_vector_store(persist_directory: str):
    """
    Verify that the vector store was created successfully by attempting to load it.
    """
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        
        # Get collection count safely
        collection_size = vectordb._collection.count()
        print(f"Vector store verified. Contains {collection_size} embeddings.")
        return True
    except Exception as e:
        print(f"Failed to verify vector store: {str(e)}")
        return False

def preview_vector_store(persist_directory: str, num_samples: int = 3):
    """
    Preview a few entries from the vector store.
    """
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        
        # Get all documents
        results = vectordb.get()
        if results and len(results['documents']) > 0:
            print(f"\nPreviewing {min(num_samples, len(results['documents']))} documents:")
            for i in range(min(num_samples, len(results['documents']))):
                print(f"\nDocument {i+1}:")
                print("Content:", results['documents'][i][:1000], "...")  
                print("Metadata:", results['metadatas'][i])
        else:
            print("No documents found in vector store.")
            
    except Exception as e:
        print(f"Failed to preview vector store: {str(e)}")

def test_retrieval(query: str, vectordb: Chroma, k: int = 5):
    """Enhanced test retrieval that highlights table content"""
    try:
        docs = vectordb.similarity_search(query, k=k)
        
        print(f"\nQuery: {query}")
        print("\nRetrieved chunks:")
        for i, doc in enumerate(docs):
            print(f"\nChunk {i+1}:")
            print(f"Type: {'Table' if doc.metadata.get('type') == 'table' else 'Text'}")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Page: {doc.metadata['page']}")
            if doc.metadata.get('type') == 'table':
                print(f"Table Headers: {doc.metadata.get('headers', 'None')}")
        return docs
    except Exception as e:
        print(f"Error in retrieval: {str(e)}")
        return None

# [Previous verify_vector_store and preview_vector_store functions remain unchanged]

def run_test_queries(vectordb: Chroma, queries: Optional[List[str]] = None):
    """Run test queries with enhanced table awareness"""
    if queries is None:
        queries = [
            "What is the initial access vector for Muggle-4?",
            "What are the credentials for rachel.mullens?",
            "Wht is the date range for the attack chain?",
            "What items were exfiltrated from the network?",
            "What user accounts were compromised during the attack?",
            "Was Cobalt Strike used in the attack chain?",
            "Did the attack chain use any DNS beacons?",
        ]
    
    print("\n=== Testing Retrieval Quality ===")
    for query in queries:
        test_retrieval(query, vectordb)
        print("\n" + "="*50)

if __name__ == "__main__":
    pdf_path = "MDS1.pdf"
    persist_dir = "chroma_db"
    
    try:
        vectordb = create_vector_store(pdf_path, persist_dir)
        print(f"Successfully created vector store at {persist_dir}")

        if verify_vector_store(persist_dir):
            preview_vector_store(persist_dir)
            run_test_queries(vectordb)
            
        else:
            print("Warning: Vector store verification failed!")
            
    except Exception as e:
        print(f"Failed to create vector store: {str(e)}")