import logging
from typing import Dict, List, Union
from pathlib import Path
from typing import List, Dict, Union
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class Chunk:
    text: str
    doc_id: int
    chunk_id: int
    metadata: Dict

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _create_chunks(self, text: str, doc_id: int, metadata: Dict) -> List[Chunk]:
      chunks = []
      current_chunk = ""
      current_size = 0
      chunk_id = 0

      words = text.split()
      for word in words:
          word += " "  # Add a space for word boundary
          word_size = len(word)

          if current_size + word_size > self.chunk_size:
              chunks.append(Chunk(
                  text=current_chunk.strip(),
                  doc_id=doc_id,
                  chunk_id=chunk_id,
                  metadata=metadata
              ))
              chunk_id += 1
              current_chunk = ""
              current_size = 0

          current_chunk += word
          current_size += word_size

      # Add the last chunk, if any
      if current_chunk:
          chunks.append(Chunk(
              text=current_chunk.strip(),
              doc_id=doc_id,
              chunk_id=chunk_id,
              metadata=metadata
          ))

      return chunks

    def process_documents(self, documents: List[Dict]) -> List[Chunk]:
        """Process preprocessed documents into chunks."""
        all_chunks = []
        for doc in documents:
            metadata = {
                'filename': doc['filename'],
                'timestamp': doc['timestamp']
            }
            doc_chunks = self._create_chunks(
                text=doc['content'],
                doc_id=doc['doc_id'],
                metadata=metadata
            )
            all_chunks.extend(doc_chunks)
        return all_chunks

    def get_chunk_info(self, chunks: List[Chunk]) -> Dict:
        """Get statistics about the chunks."""
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(len(c.text) for c in chunks) / len(chunks),
            'chunks_per_doc': {
                doc_id: len([c for c in chunks if c.doc_id == doc_id])
                for doc_id in set(c.doc_id for c in chunks)
            }
        }

class DataPreprocessor:
  def __init__(self):
    pass

  def _validate_documents(self, documents: Union[str, List[str], Union[Path, List[Path]]]) -> List[str]:
    SUPPORTED_FORMATS = {'.md', '.csv', '.json', '.txt'}

    try:
        # Handle Path inputs
        if isinstance(documents, (Path, list)):
            # Convert single Path to list
            if isinstance(documents, Path):
                documents = [documents]

            # Process list of Paths
            if all(isinstance(doc, Path) for doc in documents):
                processed_docs = []
                for doc in documents:
                    if not doc.exists():
                        raise ValueError(f"[-] File not found: {doc}")
                    if doc.suffix not in SUPPORTED_FORMATS:
                        raise ValueError(f"[-] Format not {doc.suffix} supported.")
                    processed_docs.append(doc.read_text(encoding='utf-8'))
                documents = processed_docs

        # Handle string input
        if isinstance(documents, str):
            documents = [documents]

        # Validate and filter documents
        valid_docs = [doc for doc in documents if doc.strip()]
        return valid_docs

    except ValueError as e:
        logging.error(e)
        raise

  def _clean_text(self, text: str) -> str:
    cleaned = text.replace('\n', ' ')  # Replace newlines with spaces
    cleaned = ' '.join(cleaned.split())  # Remove extra whitespace
    return cleaned.strip()

  def preprocess_documents(self, documents: Union[str, List[str], Path]) -> dict:
    # (1) load and validate each input
    validated_document_text = self._validate_documents(documents)
    print(f"[+] First 500 characters BEFORE Preprocessing text")
    for i, doc in enumerate(validated_document_text, 1):
      print(f"[+] Document {i}: {doc[:500]}")

    print(f"=" * 500)

    # (2) process each document: parsing, formatting, deletion etc.
    processed_docs = []

    # tagging on metadata
    for i, doc in enumerate(validated_document_text):
      clean_content = self._clean_text(doc)
      doc_info = {
          'content': clean_content,
          'doc_id': i,
          'filename': documents[i].name if isinstance(documents[i], Path) else f"doc_{i}",
          'timestamp': documents[i].stat().st_mtime if isinstance(documents[i], Path) else None
      }
      processed_docs.append(doc_info)

      print(processed_docs[i])

    return processed_docs
  

def main():
    preprocessor = DataPreprocessor()
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)

    doc = Path('data/MDS1.md')
    documents = [doc]

    validated_docs = preprocessor.preprocess_documents(documents)
    chunks = chunker.process_documents(validated_docs)
    chunk_stats = chunker.get_chunk_info(chunks)
    print(chunk_stats)
    print(chunks[1])
    print(chunks[1].text)

    chunks_list = []
    for chunk in chunks:
        chunks_list.append(f'"{chunk.text}"')

    print('[' + ',\n'.join(chunks_list) + ']')

if __name__ == "__main__":
   main()