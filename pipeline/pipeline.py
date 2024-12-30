"""
Execute both transform and load steps for cyber white cell documents with robust management
/////
use update pipline to be its own class, integrate those class methods into chatbot

data extraction and validation
- extract and import data into DB, if data filename already exists then omit from extraction

data chunking
- read in DB by each doc_id via SQLITE, create chunks based on chunking class, write out chunks to DB document_chunks table

data embedding
- read in DB by doc_id and process all chunks to determine their embeddings values. Read in all chunk_ids and execute ranking method/similarity search.

query processing
- 



"""
import sqlite3 as sq
import os
from datetime import datetime
import hashlib
import json

class PipelineManager:
    def create_tables(self, c):
        """Create all necessary tables for robust document management"""
        
        # Main documents table (enhanced version)
        c.execute('''CREATE TABLE IF NOT EXISTS cyber_docs (
            doc_id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            doc_type TEXT,
            event_name TEXT,
            content TEXT,
            current_version INTEGER DEFAULT 1,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Document versions table
        c.execute('''CREATE TABLE IF NOT EXISTS document_versions (
            version_id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            version_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            hash_value TEXT NOT NULL,
            modified_by TEXT,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            change_description TEXT,
            FOREIGN KEY (doc_id) REFERENCES cyber_docs(doc_id)
        )''')
        
        # Document chunks table
        c.execute('''CREATE TABLE IF NOT EXISTS document_chunks (
            chunk_id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            chunk_content TEXT NOT NULL,
            chunk_index INTEGER,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doc_id) REFERENCES cyber_docs(doc_id)
        )''')
        
        # Audit log table
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            action_type TEXT NOT NULL,
            action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            details TEXT,
            FOREIGN KEY (doc_id) REFERENCES cyber_docs(doc_id)
        )''')
        
        # Processing status table
        c.execute('''CREATE TABLE IF NOT EXISTS processing_status (
            status_id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            process_type TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY (doc_id) REFERENCES cyber_docs(doc_id)
        )''')

    def calculate_hash(self, content):
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def load(self, file_path):
        print(os.getcwd())
        conn = sq.connect('cyber_docs.db')
        c = conn.cursor()
        
        # Create all necessary tables
        self.create_tables(c)

        try:
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            event_name = filename.replace('.md', '_Event')
            content_hash = self.calculate_hash(content)
            
            # Start transaction
            c.execute('BEGIN TRANSACTION')
            
            # Insert main document
            c.execute('''
                INSERT INTO cyber_docs (filename, doc_type, event_name, content)
                VALUES (?, ?, ?, ?)
            ''', (filename, 'white_cell', event_name, content))
            
            doc_id = c.lastrowid
            
            # Store initial version
            c.execute('''
                INSERT INTO document_versions (
                    doc_id, version_number, content, hash_value, 
                    modified_by, change_description
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (doc_id, 1, content, content_hash, 'system', 'Initial version'))
            
            # Log the action
            c.execute('''
                INSERT INTO audit_log (doc_id, action_type, user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (doc_id, 'CREATE', 'system', 'Initial document creation'))
            
            # Record processing status
            c.execute('''
                INSERT INTO processing_status (
                    doc_id, process_type, status, completed_at
                ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (doc_id, 'INITIAL_LOAD', 'COMPLETED'))
            
            # Commit transaction
            conn.commit()
            print(f"Successfully loaded {filename}")
            
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            conn.rollback()
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def verify_database(self):
        """Verify database integrity and print summary"""
        conn = sq.connect('cyber_docs.db')
        c = conn.cursor()
        
        print("\nDatabase Summary:")
        
        # Check documents
        c.execute("SELECT COUNT(*) FROM cyber_docs")
        doc_count = c.fetchone()[0]
        print(f"Total Documents: {doc_count}")
        
        # Check versions
        c.execute("SELECT COUNT(*) FROM document_versions")
        version_count = c.fetchone()[0]
        print(f"Total Versions: {version_count}")
        
        # Check audit log
        c.execute("SELECT COUNT(*) FROM audit_log")
        audit_count = c.fetchone()[0]
        print(f"Audit Log Entries: {audit_count}")
        
        # Print recent activities
        print("\nRecent Activities:")
        c.execute('''
            SELECT action_timestamp, action_type, details 
            FROM audit_log 
            ORDER BY action_timestamp DESC 
            LIMIT 5
        ''')
        activities = c.fetchall()
        for activity in activities:
            print(f"- {activity[0]}: {activity[1]} - {activity[2]}")
        
        conn.close()

def main():
    
    mngr = PipelineManager()

    documents = [
        "data/MDS1.md",
        "data/COMRADE_TURLA.md",
    ]
    
    for doc in documents:
        mngr.load(doc)
    
    mngr.verify_database()

if __name__ == "__main__":
    main()