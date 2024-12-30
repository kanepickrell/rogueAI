"""
Extract some dataset locally or from a URL. MD, CSV, or JSON will be fine

white cell dataset
"""
import pydantic

def extract(filename: str):
    with open(filename, 'r') as f:
        content = f.read()
        print(content)

        
def main():
    extract("../data/COMRADE_TURLA.md")

if __name__ == "__main__":
    main()
