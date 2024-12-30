# Initial setup for RAG implementation
import os
import openai
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Check if OPENAI_API_KEY is set
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("Error: OPENAI_API_KEY is not set in the environment. Please set it in the .env file.")

# Set OpenAI key and model
openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai.api_key)
model_name = "gpt-4"

def get_or_create_vector_store(client, vector_store_name):
    """Create or retrieve a vector store for document storage"""
    if not vector_store_name:
        raise ValueError("Error: 'vector_store_name' is not set. Please provide a valid vector store name.")
    
    try:
        # List all existing vector stores
        vector_stores = client.beta.vector_stores.list()
        
        # Check if the vector store with the given name already exists
        for vector_store in vector_stores.data:
            if vector_store.name == vector_store_name:
                print(f"Vector Store '{vector_store_name}' already exists with ID: {vector_store.id}")
                return vector_store
        
        # Create a new vector store if it doesn't exist
        vector_store = client.beta.vector_stores.create(name=vector_store_name)
        print(f"New vector store '{vector_store_name}' created with ID: {vector_store.id}")
        return vector_store
        
    except Exception as e:
        print(f"Error creating or retrieving vector store: {e}")
        return None

def upload_pdfs_to_vector_store(client, vector_store_id, directory_path='Upload'):
    """Upload PDFs from the specified directory to the vector store"""
    try:
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Error: Directory '{directory_path}' does not exist.")
        
        if not os.listdir(directory_path):
            raise ValueError(f"Error: Directory '{directory_path}' is empty. No files to upload.")
        
        file_ids = {}
        # Get all PDF file paths from the directory
        file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) 
                     if file.endswith(".pdf")]
        
        # Check if there are any PDFs to upload
        if not file_paths:
            raise ValueError(f"Error: No PDF files found in directory '{directory_path}'.")
        
        # Iterate through each file and upload to vector store
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                uploaded_file = client.beta.vector_stores.files.upload(
                    vector_store_id=vector_store_id, 
                    file=file
                )
                print(f"Uploaded file: {file_name} with ID: {uploaded_file.id}")
                file_ids[file_name] = uploaded_file.id
                
        print(f"All files have been successfully uploaded to vector store with ID: {vector_store_id}")
        return file_ids
        
    except Exception as e:
        print(f"Error uploading files to vector store: {e}")
        return None

# Initialize vector store
if __name__ == "__main__":
    vector_store_name = "rag_docs_store"  # You can change this name
    vector_store = get_or_create_vector_store(client, vector_store_name)
    
    if vector_store:
        # Upload PDFs if vector store was created successfully
        file_ids = upload_pdfs_to_vector_store(client, vector_store.id)
        print("Vector store setup completed successfully.")
    else:
        print("Failed to setup vector store.")
