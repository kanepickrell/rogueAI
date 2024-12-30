from img2table.document import PDF
from img2table.ocr import TesseractOCR
import pandas as pd
from pathlib import Path
import logging

class TableExtractor:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def extract_tables(self, pdf_path: str):
        """
        Extract tables from PDF using img2table's recommended approach
        """
        try:
            # Initialize OCR
            ocr = TesseractOCR(n_threads=4, lang="eng")
            
            # Load PDF with text extraction enabled
            pdf = PDF(
                src=pdf_path,
                pdf_text_extraction=True,  # Try native text first
                detect_rotation=True       # Handle rotated tables
            )
            
            # Extract tables with all features enabled
            tables = pdf.extract_tables(
                ocr=ocr,
                implicit_rows=True,        # Handle implicit separators
                implicit_columns=True,
                borderless_tables=True,    # Get both bordered and borderless
                min_confidence=50
            )
            
            # Process extracted tables
            processed_tables = []
            
            for page_num, page_tables in tables.items():
                for table_idx, table in enumerate(page_tables, 1):
                    # Get DataFrame and check if valid
                    if not table.df.empty:
                        table_info = {
                            'table_id': f"table_{page_num+1}_{table_idx}",
                            'page': page_num + 1,
                            'position': {
                                'x1': table.bbox.x1,
                                'y1': table.bbox.y1,
                                'x2': table.bbox.x2,
                                'y2': table.bbox.y2
                            },
                            # Keep both formats as recommended in the thread
                            'markdown': table.df.to_markdown(index=False),
                            'text': self._df_to_text(table.df),
                            'dataframe': table.df
                        }
                        processed_tables.append(table_info)
            
            return processed_tables
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            return None
            
    def _df_to_text(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to text format, preserving structure
        """
        text_parts = []
        
        # Add column headers
        text_parts.append(f"Columns: {', '.join(str(col) for col in df.columns)}")
        
        # Add each row
        for idx, row in df.iterrows():
            row_items = []
            for col in df.columns:
                value = row[col]
                if pd.notna(value):  # Only include non-null values
                    row_items.append(f"{col}: {value}")
            text_parts.append(" | ".join(row_items))
            
        return "\n".join(text_parts)

def process_pdf_tables(pdf_path: str, output_dir: Path = None):
    """
    Process tables from PDF and optionally save results
    """
    extractor = TableExtractor()
    tables = extractor.extract_tables(pdf_path)
    
    if not tables:
        print("No tables found or error in processing")
        return
    
    print(f"Found {len(tables)} tables")
    
    # Process each table
    for table in tables:
        print(f"\nTable {table['table_id']} on page {table['page']}")
        print("\nMarkdown format:")
        print(table['markdown'])
        print("\nText format:")
        print(table['text'])
        
        # Save if output directory provided
        if output_dir:
            table_dir = output_dir / table['table_id']
            table_dir.mkdir(parents=True, exist_ok=True)
            
            # Save formats
            with open(table_dir / 'table.md', 'w') as f:
                f.write(table['markdown'])
            
            with open(table_dir / 'table.txt', 'w') as f:
                f.write(table['text'])
            
            # Save DataFrame
            table['dataframe'].to_csv(table_dir / 'table.csv', index=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract tables from PDF for RAG')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', '-o', help='Output directory for extracted tables')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    process_pdf_tables(args.pdf_path, output_dir)