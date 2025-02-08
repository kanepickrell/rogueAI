import os
import openai

# Set your OpenAI API key
API_KEY = "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"
openai.api_key = API_KEY 

filepath = "mjml_templates/black-friday.mjml"

def extract_mjml_from_file(file_path):
    """
    Reads an MJML file and returns its content.
    """
    with open(file_path, 'r') as file:
        text = file.read()
    return text

def transform(mjml_text):
    """
    Sends a chat request with the provided MJML content and returns the response.
    The AI is instructed to output only the basic HTML skeleton without any pictures or styles.
    """
    messages = [
        {
            "role": "system", 
            "content": (
                "You are an expert web developer. You will be given an MJML webpage. "
                "Your task is to extract only the basic HTML skeleton of the webpage—removing all pictures, styles, and formatting. "
                "Provide only the bare structure (e.g., HTML tags that define the layout) without any inline styles or images."
            )
        },
        {
            "role": "user", 
            "content": f"Convert the following MJML webpage into its basic HTML skeleton (no pictures or styles, just the structure):\n\n{mjml_text}"
        }
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Update the model name as required
        messages=messages
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Extract MJML content from file
    mjml_content = extract_mjml_from_file(filepath)
    
    # Send the chat request and get the model's response
    response_content = transform(mjml_content)
    print("\nResponse from model:")
    print(response_content)
    
    # Define output folder and ensure it exists
    output_folder = "base_layer"
    os.makedirs(output_folder, exist_ok=True)
    
    # Create an output file name based on the input file name
    filename = os.path.basename(filepath)
    base_name, _ = os.path.splitext(filename)
    output_filename = f"{base_name}_base_layer.html"
    output_path = os.path.join(output_folder, output_filename)
    
    # Save the base layer to the output file
    with open(output_path, 'w') as output_file:
        output_file.write(response_content)
    
    print(f"\nSaved base layer to: {output_path}")
