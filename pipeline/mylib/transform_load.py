"""
Execute both transform and load steps for cyber white cell documents
"""
import sqlite3 as sq
import os
from datetime import datetime

def load(file_path):
    print(os.getcwd())
    conn = sq.connect('cyber_docs.db')
    c = conn.cursor()
    
    # Create table with proper schema
    c.execute('''CREATE TABLE IF NOT EXISTS cyber_docs (
        doc_id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        doc_type TEXT,
        event_name TEXT,
        content TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    try:
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Get filename from path
        filename = os.path.basename(file_path)
        
        # Determine event name from filename (removing .md extension)
        event_name = filename.replace('.md', '_Event')
        
        # Insert document
        c.execute('''
            INSERT INTO cyber_docs (filename, doc_type, event_name, content)
            VALUES (?, ?, ?, ?)
        ''', (filename, 'white_cell', event_name, content))
        
        print(f"Successfully loaded {filename}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error loading document: {str(e)}")
    finally:
        conn.commit()
        conn.close()

def main():
    # Load each document
    documents = [
        "../data/MDS1.md",
        "../data/COMRADE_TURLA.md",
        "../data/567_OGV.md"
    ]
    
    for doc in documents:
        load(doc)
        
    # Verify loading
    conn = sq.connect('cyber_docs.db')
    c = conn.cursor()
    c.execute("SELECT filename, event_name FROM cyber_docs")
    loaded_docs = c.fetchall()
    print("\nLoaded documents:")
    for doc in loaded_docs:
        print(f"- {doc[0]}: {doc[1]}")
    conn.close()

if __name__ == "__main__":
    main()