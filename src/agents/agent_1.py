import openai
import json
import time
from typing import List, Dict, Any
import cv2
import numpy as np
import pytesseract
from PIL import Image

class VisualizationAgent:
    def __init__(self, api_key: str):
        """Initialize the agent with OpenAI API key."""
        self.api_key = api_key
        openai.api_key = api_key
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        
    def extract_text_from_image(self, image_path:
                                 str) -> List[Dict[str, float]]:
        """Extract text from image using advanced OCR and contour detection."""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply OTSU threshold
            ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
            
            # Define kernel for contour detection
            rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
            
            # Apply dilation
            dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
            
            # Find contours
            contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            # Sort contours top-to-bottom
            contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
            
            # Extract text from each contour
            data_points = []
            current_row = {}
            
            print("\nProcessing contours:")  # Debug output
            # print(f"number of contours: {len(contours)}")  # Debug output
            for idx, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Crop the text block
                cropped = img[y:y + h, x:x + w]
                
                # Apply OCR on the cropped image
                text = pytesseract.image_to_string(cropped).strip()
                print(f"Contour {idx}: Position(x={x}, y={y}), Text='{text}'")  # Debug print
                
                # Try to convert to number if it's not a header
                if not ('x' in text.lower() or 'y' in text.lower()):
                    try:
                        num = float(text)
                        if 'x' not in current_row:
                            current_row['x'] = num
                        elif 'y' not in current_row:
                            current_row['y'] = num
                            data_points.append(current_row)
                            current_row = {}
                    except ValueError:
                        continue
            
            print(f"\nExtracted data points: {json.dumps(data_points, indent=2)}")
            return data_points
            
        except Exception as e:
            print(f"Error in extract_text_from_image: {str(e)}")
            return []

    def process_data(self, data_points: List[Dict[str, float]]) -> Dict[str, Any]:
        """Convert extracted data points into visualization format."""
        return {
            "x_values": [p['x'] for p in data_points if 'x' in p and 'y' in p],
            "y_values": [p['y'] for p in data_points if 'x' in p and 'y' in p],
            "x_label": "X",
            "y_label": "Y"
        }

    def create_visualization(self, image_path: str) -> Dict[str, Any]:
        """Main method to extract data from image."""
        try:
            # Extract data points
            data_points = self.extract_text_from_image(image_path)
            if not data_points:
                return {"error": "No valid data points extracted from image"}
            
            # Process into visualization format
            data = self.process_data(data_points)
            
            return {
                "data": data,
                "message": "Data extracted successfully"
            }
        except Exception as e:
            print(f"Error in create_visualization: {str(e)}")
            return {"error": str(e)}
        
    def read_image(self, image_path: str):
        # Opening the image & storing it in an image object 
        img = Image.open(image_path) 
    
        # text = pytesseract.image_to_string(img) 
        text = pytesseract.image_to_data(Image.open(image_path), lang='eng', config='--psm 11', output_type=pytesseract.Output.DICT)
        
        # Displaying the extracted text 
        print(text)

# Example usage
if __name__ == "__main__":
    API_KEY = "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"
    agent = VisualizationAgent(API_KEY)
    image_path = "image3.PNG"
    
    print("Processing image:", image_path)
    print("-" * 50)
    
    # result = agent.create_visualization(image_path)
    # print("\nResult:", json.dumps(result, indent=2))

    result = agent.read_image(image_path)
    # print("\nResult:", result)
