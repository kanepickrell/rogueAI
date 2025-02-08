from swarm import Swarm, Agent
import base64
import os
from PIL import Image
import io
import re

client = Swarm()

# Define directories
RAW_IMAGE_DIR = "./img/raw"
ENCODED_IMAGE_DIR = "./img/encoded"
HTML_OUTPUT_DIR = "./html_pages"

# Ensure output directories exist
os.makedirs(ENCODED_IMAGE_DIR, exist_ok=True)
os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Image Processing Functions
# ---------------------------

def find_image(image_name):
    """Searches for an image file in the RAW_IMAGE_DIR.
    
    It extracts only the file name in case the image_name contains extra path components.
    """
    base_name = os.path.basename(image_name)  # Ensure we only use the filename.
    image_path = os.path.join(RAW_IMAGE_DIR, base_name)
    print(f"Looking for image at: {image_path}")
    return image_path if os.path.exists(image_path) else None

def resize_image(image_path, max_size=(300, 300)):
    """Resizes the image to prevent large Base64 output."""
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()  # Return binary image data

def image_to_base64(image_name):
    """
    Encodes the resized image to Base64 and writes it to ENCODED_IMAGE_DIR.
    Returns a confirmation message.
    """
    image_path = find_image(image_name)
    if image_path:
        image_data = resize_image(image_path)
        encoded_string = base64.b64encode(image_data).decode("utf-8")
        safe_filename = re.sub(r'\W+', '_', image_name) + ".txt"
        output_file_path = os.path.join(ENCODED_IMAGE_DIR, safe_filename)
        with open(output_file_path, "w") as file:
            file.write(encoded_string)
        return f"Base64 string saved to {output_file_path}"
    return "Image not found."

def get_base64_string(image_name):
    """
    Returns the Base64 string of the resized image.
    Also saves the encoded string to disk.
    """
    image_path = find_image(image_name)
    if image_path:
        image_data = resize_image(image_path)
        encoded_string = base64.b64encode(image_data).decode("utf-8")
        safe_filename = re.sub(r'\W+', '_', image_name) + ".txt"
        output_file_path = os.path.join(ENCODED_IMAGE_DIR, safe_filename)
        with open(output_file_path, "w") as file:
            file.write(encoded_string)
        return encoded_string
    return None

# ---------------------------
# HTML Processing Functions
# ---------------------------

def save_html_to_file(html_content, file_name):
    """
    Saves the provided HTML content to a file within the HTML_OUTPUT_DIR.
    :param html_content: String containing the HTML content.
    :param file_name: Desired file name (without extension).
    :return: The path to the saved HTML file.
    """
    safe_filename = re.sub(r'\W+', '_', file_name.lower()) + ".html"
    html_file_path = os.path.join(HTML_OUTPUT_DIR, safe_filename)
    with open(html_file_path, "w") as html_file:
        html_file.write(html_content)
    return html_file_path

def embed_images_in_html(html_content):
    """
    Ensures that all images in the HTML are embedded via Base64.
    
    It does two things:
      1. Replaces placeholders of the form:
           <!-- IMAGE: image_filename -->
         with <img> tags containing Base64 data URIs.
      2. Finds any <img> tags whose src attributes reference image files (e.g. "dingo.png")
         and replaces the src value with the corresponding Base64 data URI.
    """
    # First, replace comment placeholders.
    pattern_comment = r"<!--\s*IMAGE:\s*(\S+)\s*-->"
    matches = re.findall(pattern_comment, html_content)
    for image_name in matches:
        base64_string = get_base64_string(image_name)
        if base64_string:
            img_tag = f'<img src="data:image/png;base64,{base64_string}" alt="{image_name}">'
        else:
            img_tag = f'<p>Image {image_name} not found.</p>'
        # Use re.IGNORECASE to catch variations in case.
        html_content = re.sub(r"<!--\s*IMAGE:\s*" + re.escape(image_name) + r"\s*-->",
                              img_tag, html_content, flags=re.IGNORECASE)
    
    # Next, check for any <img> tags that use a file name as the source.
    pattern_img = r'(<img\s+[^>]*src=["\'])([^"\']+\.(?:png|jpg|jpeg|gif))(["\'][^>]*>)'
    def repl_img(match):
        prefix = match.group(1)
        image_src = match.group(2)
        suffix = match.group(3)
        print(f"Attempting to embed image: {image_src}")
        base64_string = get_base64_string(image_src)
        if base64_string:
            print(f"Successfully encoded {image_src} ({len(base64_string)} characters)")
            return f'{prefix}data:image/png;base64,{base64_string}{suffix}'
        else:
            print(f"Failed to encode {image_src}")
            return match.group(0)
    html_content = re.sub(pattern_img, repl_img, html_content, flags=re.IGNORECASE)
    
    return html_content

# ---------------------------
# Screenshot Functions
# ---------------------------

def screenshot_rendered_page(html_file_path, screenshot_file_path="final_website.png"):
    """
    Opens the given HTML file in a headless browser and takes a screenshot of the rendered website.
    :param html_file_path: Path to the HTML file to render.
    :param screenshot_file_path: File path where the screenshot image will be saved.
    :return: The path to the saved screenshot image.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,800")
    
    # Initialize the Chrome webdriver (make sure chromedriver is installed or specify its path).
    driver = webdriver.Chrome(options=chrome_options)
    
    # Load the local HTML file.
    file_url = "file:///" + os.path.abspath(html_file_path)
    driver.get(file_url)
    
    # Optional: wait for the page to load completely (e.g., time.sleep(1))
    driver.save_screenshot(screenshot_file_path)
    driver.quit()
    
    return screenshot_file_path

def encode_image_to_base64(image_path):
    """
    Reads an image file and returns its Base64-encoded string.
    :param image_path: Path to the image file.
    :return: Base64-encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# ---------------------------
# Agent Definitions
# ---------------------------

# Agent A: Responsible for image conversion.
agent_a = Agent(
    name="Agent A",
    instructions="""
        You are an HTML transformation assistant. Your primary responsibilities include:
        - Finding and encoding images to Base64, storing the output in ./img/encoded/.
        - Handling requests for either task independently or performing both as part of a complete workflow.
        - Ensuring all output is saved to the correct directory without needing external API calls.
        
        Respond dynamically to user requests. If only Base64 encoding is needed, perform that task.
        If an HTML page is required, generate it with the requested image.
        If both tasks are necessary, handle them sequentially.
    """,
    functions=[image_to_base64],
    function_execution_mode="local"
)

# Agent B: Responsible for designing the base HTML.
agent_b = Agent(
    name="Agent B",
    instructions="""
        You are responsible for structuring the foundational HTML layer of a webpage based on a given description.
        - You generate semantic HTML with clear sections (header, main, footer).
        - You ensure the layout is well-formed and adaptable.
        - The description will specify sections, and you must create structured content accordingly.
        - If an image is requested, include a placeholder in the form <!-- IMAGE: image_filename -->
          where image_filename is the name of the image file.
        - Your goal is to create a clean, readable, and extendable HTML base.
    """,
)

# Agent C: Responsible for adding content and styling.
agent_c = Agent(
    name="Agent C",
    instructions="""
        You are responsible for adding content and styling to the provided HTML base.
        - Your task is to take the base HTML structure (created by Agent B) and enhance it.
        - Add engaging, well-organized content to sections such as the header, main, and footer.
        - Incorporate CSS styling (either via a <style> tag or inline styles) to improve the visual appearance.
        - The page is about dingo enthusiasts. Include content about dingo history, upcoming events, and contact information.
        - Use modern typography, a dark blue and white color scheme, and responsive layout principles.
        Your final output should be a complete, styled HTML document.
    """,
)

# Agent D: Responsible for reviewing the final website using the screenshot.
agent_d = Agent(
    name="Agent D",
    instructions="""
        You are an expert design reviewer. Your task is to provide constructive feedback on the website design
        based on the provided screenshot. Evaluate the layout, color scheme, typography, and overall usability.
        Provide suggestions for improvement if necessary.
    """,
)

# ---------------------------
# Workflow Execution
# ---------------------------

# Step 1: Generate the base HTML using Agent B.
html_response = client.run(
    agent=agent_b,
    messages=[{"role": "user", "content":
        "Generate a webpage with title: The Dingo Den. Include section: Dingo Fans. "
        "Include section: Events. Include section: Contact. You must include dingo.png and smile.png images in the page."}],
)
base_html_content = html_response.messages[-1]["content"]
print("HTML generated by Agent B:")
print(base_html_content)

# Note: We intentionally skip embedding images at this stage to avoid token overflow.

# Step 2: Run Agent C to add content and styling to the base HTML.
agent_c_response = client.run(
    agent=agent_c,
    messages=[
        {"role": "user", "content":
         "Enhance the following HTML by adding engaging content and appropriate styling. "},
        {"role": "assistant", "content": base_html_content}
    ]
)
final_html_content = agent_c_response.messages[-1]["content"]
print("\nFinal HTML after content and styling added by Agent C:")
print(final_html_content)

# Step 3: Now embed images in the final HTML content.
final_html_with_images = embed_images_in_html(final_html_content)
print("\nFinal HTML after embedding images:")
print(final_html_with_images)

# Step 4: Save the final HTML content to a file.
final_output_file_path = save_html_to_file(final_html_with_images, "The_Dingo_Den_Styled")
print(f"\nFinal styled HTML page saved to {final_output_file_path}")

# Step 5: Take a screenshot of the rendered final HTML page.
screenshot_file_path = screenshot_rendered_page(final_output_file_path, "The_Dingo_Den_Screenshot.png")
print(f"\nScreenshot of the rendered website saved to {screenshot_file_path}")

# Encode the screenshot to Base64.
screenshot_base64 = encode_image_to_base64(screenshot_file_path)
print("\nScreenshot encoded as Base64 (truncated):", screenshot_base64[:100], "...")

# Step 6: Run Agent D to review the website using the screenshot.
agent_d_response = client.run(
    agent=agent_d,
    messages=[
        {"role": "user", "content":
         "Please review the following screenshot of the final website design and provide feedback and suggestions."},
        {"role": "assistant", "content": f"{screenshot_file_path}"}
    ]
)
print("\nAgent D's review of the website:")
print(agent_d_response.messages[-1]["content"])

print("\nProcess completed.")
