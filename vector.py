import os
import shutil
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores.chroma import Chroma  
import logging
from typing import Dict, List
import statistics
from collections import defaultdict
import re

def clean_directory(directory: str) -> None:
    """Safely clean a directory and its contents"""
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)

def clean_text(text: str) -> str:
    """Minimal cleaning that won't affect spelling"""
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove duplicate consecutive lines
    text = re.sub(r'^(.+)(\n\1)+', r'\1', text, flags=re.MULTILINE)
    
    # Normalize whitespace while preserving line breaks
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return '\n'.join(lines)

def create_vector_store(pdf_path: str, persist_directory: str):
    """
    Create a local vector store from a PDF document using Chroma DB.
    
    Args:
        pdf_path (str): Path to the PDF file
        persist_directory (str): Directory to store the vector database
    """
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Check if PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        # Clean existing directory if it exists
        logger.info(f"Cleaning existing directory at {persist_directory}")
        clean_directory(persist_directory)

        # Create new persist directory
        os.makedirs(persist_directory, exist_ok=True)

        # 1. Load the PDF
        logger.info(f"Loading PDF from {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        for doc in documents:
            doc.page_content = clean_text(doc.page_content)

        # 2. Split text into chunks
        logger.info("Splitting text into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,        
            chunk_overlap=100,       # Reduced overlap since chunks will be larger
            length_function=len,
                separators=[
                "\n",      # Any newline
                ". ",      # Any sentence
                ", ",      # Any clause
                " ",       # Any word
            ]
        )

        texts = text_splitter.split_documents(documents)

        # 3. Initialize embedding model
        logger.info("Initializing embedding model")
        embedding_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )

        # 4. Create and persist the vector store
        logger.info("Creating vector store")
        
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=embedding_model,
            persist_directory=persist_directory
        )
        
        logger.info(f"Vector store created and persisted to {persist_directory}")
        
        return vectordb

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        # Attempt to clean up on failure
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

#########################
#########################
#########################

class ChunkAnalyzer:
    def __init__(self, vectordb):
        self.vectordb = vectordb
        self.results = vectordb.get()
        
    def get_basic_stats(self) -> Dict:
        """Calculate basic statistics about chunks"""
        chunk_lengths = [len(doc) for doc in self.results['documents']]
        
        stats = {
            "total_chunks": len(chunk_lengths),
            "avg_chunk_length": statistics.mean(chunk_lengths),
            "min_chunk_length": min(chunk_lengths),
            "max_chunk_length": max(chunk_lengths),
            "std_dev_length": statistics.stdev(chunk_lengths) if len(chunk_lengths) > 1 else 0
        }
        
        return stats
    
    def analyze_page_distribution(self) -> Dict:
        """Analyze how chunks are distributed across pages"""
        page_counts = defaultdict(int)
        for metadata in self.results['metadatas']:
            page_counts[metadata['page']] += 1
            
        return dict(page_counts)
    
    def find_potential_issues(self) -> List[str]:
        """Identify potential issues with chunks"""
        issues = []
        
        # Check for very short chunks
        for i, doc in enumerate(self.results['documents']):
            if len(doc) < 100:  # Arbitrary threshold
                issues.append(f"Chunk {i} is very short ({len(doc)} chars)")
                
        # Check for chunks that start with headers/disclaimers
        header_indicators = ['unclassified', 'for official use only', 'fouo', 'notice']
        for i, doc in enumerate(self.results['documents']):
            if any(doc.lower().startswith(h) for h in header_indicators):
                issues.append(f"Chunk {i} starts with header/disclaimer")
                
        return issues
    
    def preview_chunks_detailed(self, num_samples: int = 3):
        """Provide detailed preview of chunks with analysis"""
        print("\n=== Chunk Analysis ===")
        
        # Basic stats
        stats = self.get_basic_stats()
        print("\nBasic Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
            
        # Page distribution
        page_dist = self.analyze_page_distribution()
        print("\nChunks per Page:")
        for page, count in sorted(page_dist.items()):
            print(f"Page {page}: {count} chunks")
            
        # Issues
        issues = self.find_potential_issues()
        if issues:
            print("\nPotential Issues Found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"- {issue}")
                
        # Content preview
        print("\nDetailed Chunk Previews:")
        for i in range(min(num_samples, len(self.results['documents']))):
            print(f"\nChunk {i+1}:")
            content = self.results['documents'][i]
            print("Length:", len(content))
            print("First 150 chars:", content[:150].replace('\n', ' '))
            print("Last 150 chars:", content[-150:].replace('\n', ' '))
            print("Metadata:", self.results['metadatas'][i])
            
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements for chunking strategy"""
        suggestions = []
        stats = self.get_basic_stats()
        
        # Add more relevant checks
        if stats['std_dev_length'] > 400:  # High variance
            suggestions.append("High variance in chunk sizes - consider adjusting splitting strategy")
        
        if stats['max_chunk_length'] - stats['min_chunk_length'] > 1000:
            suggestions.append("Large gap between shortest and longest chunks")
            
        if any(count > 1 for count in self.analyze_page_distribution().values()):
            suggestions.append("Some pages are split into multiple chunks - consider reviewing split points")
        
        # Check chunk size distribution
        ideal_chunk_size = 1000  # Your target
        if abs(stats['avg_chunk_length'] - ideal_chunk_size) > 200:
            suggestions.append(f"Average chunk size deviates significantly from target {ideal_chunk_size}")
        
        return suggestions

def analyze_vector_store(persist_directory: str):
    """Analyze the vector store contents"""
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        
        analyzer = ChunkAnalyzer(vectordb)
        analyzer.preview_chunks_detailed()
        
        print("\nSuggested Improvements:")
        for suggestion in analyzer.suggest_improvements():
            print(f"- {suggestion}")
            
    except Exception as e:
        print(f"Failed to analyze vector store: {str(e)}")

if __name__ == "__main__":
    # Example usage
    pdf_path = "MDS1.pdf"  # Your PDF path
    persist_dir = "chroma_db"  # Directory where the vector store will be saved
    
    try:
        vectordb = create_vector_store(pdf_path, persist_dir)
        print(f"Successfully created vector store at {persist_dir}")

        if verify_vector_store(persist_dir):
            # Preview some of the stored documents
            preview_vector_store(persist_dir)
        else:
            print("Warning: Vector store verification failed!")


        # analyze_vector_store(persist_dir)
        
            
    except Exception as e:
        print(f"Failed to create vector store: {str(e)}")