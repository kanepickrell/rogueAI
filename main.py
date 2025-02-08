#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

def setup_paths():
    """Add src directory to Python path"""
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.append(str(src_path))

def parse_args():
    parser = argparse.ArgumentParser(description='RogueAI - Training Event Analysis Chatbot')
    parser.add_argument('--mode', choices=['chat', 'pipeline'], default='chat',
                      help='Run mode: chat (UI) or pipeline (data processing)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    return parser.parse_args()

def main():
    # Setup project paths
    setup_paths()
    
    # Parse command line arguments
    args = parse_args()
    
    if args.mode == 'chat':
        # Run streamlit directly
        os.system('streamlit run src/chatbot/app.py')
    else:
        # Import and run pipeline
        print("Pipeline mode is not implemented yet.")

if __name__ == "__main__":
    main()