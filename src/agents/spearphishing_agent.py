import json
import subprocess
import tempfile
from jinja2 import Template
from bs4 import BeautifulSoup
import os
from swarm import Agent, Swarm
import re


# Make sure our npm global folder is in PATH
os.environ["PATH"] += os.pathsep + r"C:/Users/kanep/AppData/Roaming/npm"

# ------------------------------------------------------------
# Helper: Extract JSON from Agent Output
# ------------------------------------------------------------
def extract_json_from_output(text: str) -> str:
    """
    If the text contains a markdown code block with JSON,
    extract the JSON string; otherwise, return the trimmed text.
    """
    pattern = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1)
    return text.strip()

# ------------------------------------------------------------
# Step 1: Gather Intelligence
# ------------------------------------------------------------
def gather_intelligence(profile_json: str) -> str:
    profile = json.loads(profile_json)
    company = profile.get("company", "")
    interests = profile.get("interests", [])
    profile["news"] = [{
        "query": f"{company} recent news",
        "url": f"https://news.example.com/{company.lower().replace(' ', '-')}",
        "snippet": f"{company} has recently launched an innovative product line."
    }]
    return json.dumps(profile, indent=2)

# ------------------------------------------------------------
# Step 2: Generate Persona (Email Content)
# ------------------------------------------------------------
def generate_persona(profile_json: str) -> str:
    profile = json.loads(profile_json)
    company = profile.get("company", "Unknown Corp")
    target_name = profile.get("name", "Valued Partner")
    news_item = profile.get("news", [{}])[0]
    persona = {
        "company": company,
        "target_name": target_name,
        "sender_name": "David Thompson",
        "sender_email": f"david.thompson@{company.lower().replace(' ', '')}.com",
        "sender_position": "Corporate Communications Manager",
        "subject": f"Important Update from {company}",
        "message_intro": f"I was excited to see that {company} has been in the news lately.",
        "message_body": f"We are reaching out to share details regarding {news_item.get('snippet', 'our latest developments')}. "
                        "We believe this update could open up new opportunities for collaboration.",
        "cta_link": f"https://{company.lower().replace(' ', '')}.com/update"
    }
    return json.dumps(persona, indent=2)

# ------------------------------------------------------------
# Step 3: Generate Imagery (Visual Assets)
# ------------------------------------------------------------
def generate_imagery(profile_json: str) -> str:
    profile = json.loads(profile_json)
    company = profile.get("company", "Unknown Corp")
    imagery = {
        "logo_url": f"https://{company.lower().replace(' ', '')}.com/assets/logo.png",
        "banner_url": f"https://{company.lower().replace(' ', '')}.com/assets/banner.jpg",
        "layout": {
            "logo": {"width": "150px", "alt": f"{company} Logo"},
            "banner": {"width": "100%", "alt": f"{company} Newsletter Banner"}
        }
    }
    return json.dumps(imagery, indent=2)

# ------------------------------------------------------------
# Helper: Convert MJML to HTML using the MJML CLI
# ------------------------------------------------------------
def convert_mjml_to_html(mjml_str: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".mjml", delete=False) as mjml_file:
        mjml_file.write(mjml_str)
        mjml_file.flush()
        input_filename = mjml_file.name

    with tempfile.NamedTemporaryFile(mode="r", suffix=".html", delete=False) as html_file:
        output_filename = html_file.name

    try:
        subprocess.run(["mjml.cmd", input_filename, "-o", output_filename], check=True)
        with open(output_filename, "r") as f:
            html_output = f.read()
    except subprocess.CalledProcessError as e:
        html_output = f"Error during MJML conversion: {e}"
    return html_output

# ------------------------------------------------------------
# New Step: Analyze Images (Simulated)
# ------------------------------------------------------------
def analyze_images() -> dict:
    suggestions = {
        "dominant_color": "#0055aa",
        "font_family": "Roboto, 'Helvetica Neue', Arial, sans-serif",
        "cta_bg_color": "#ff5500",
        "body_bg_image": "https://example.com/updated-background.jpg"
    }
    return suggestions

# ------------------------------------------------------------
# New Step: Design Improvement Agent
# ------------------------------------------------------------
def design_improvement_agent(persona_json: str, imagery_json: str) -> str:
    style_suggestions = analyze_images()
    persona = json.loads(persona_json)
    imagery = json.loads(imagery_json)
    
    mjml_template_str = """
    <mjml>
      <mj-head>
        <mj-attributes>
          <mj-all font-family="{{ font_family }}" color="#333333" />
          <mj-class name="cta" background-color="{{ cta_bg_color }}" color="#ffffff" padding="15px 30px" border-radius="4px" font-size="16px" font-weight="bold" text-transform="uppercase" />
        </mj-attributes>
        <mj-style inline="inline">
          .body-background {
            background-image: url('{{ body_bg_image }}');
            background-repeat: no-repeat;
            background-size: cover;
          }
        </mj-style>
      </mj-head>
      <mj-body css-class="body-background" background-color="#f2f2f2">
        <mj-section padding="20px">
          <mj-column>
            <mj-image width="120px" src="{{ logo_url }}" alt="{{ company }} Logo" align="center" />
            <mj-text align="center" font-size="24px" font-weight="bold" padding-top="10px">{{ company }} Newsletter</mj-text>
          </mj-column>
        </mj-section>
        <mj-section background-color="#ffffff" padding="30px" border-radius="8px" css-class="main-content">
          <mj-column>
            <mj-text font-size="16px" line-height="1.6" padding-bottom="20px">
              Dear {{ target_name }},<br/><br/>
              {{ message_intro }}<br/><br/>
              {{ message_body }}
            </mj-text>
            <mj-button css-class="cta" href="{{ cta_link }}">Learn More</mj-button>
          </mj-column>
        </mj-section>
        <mj-section padding="20px">
          <mj-column>
            <mj-text align="center" font-size="12px" color="#888888">
              Best regards,<br/>
              {{ sender_name }} | {{ sender_position }}<br/>
              {{ company }}
            </mj-text>
          </mj-column>
        </mj-section>
      </mj-body>
    </mjml>
    """
    template = Template(mjml_template_str)
    rendered_mjml = template.render(
        logo_url=imagery.get("logo_url", ""),
        company=persona.get("company", "Your Company"),
        target_name=persona.get("target_name", "Valued Partner"),
        message_intro=persona.get("message_intro", "We have an exciting update to share with you."),
        message_body=persona.get("message_body", "Please see the details below for more information."),
        cta_link=persona.get("cta_link", "#"),
        sender_name=persona.get("sender_name", "Sender Name"),
        sender_position=persona.get("sender_position", "Sender Position"),
        font_family=style_suggestions.get("font_family", "Roboto, 'Helvetica Neue', Arial, sans-serif"),
        cta_bg_color=style_suggestions.get("cta_bg_color", "#007bff"),
        body_bg_image=style_suggestions.get("body_bg_image", "https://example.com/your-background.jpg")
    )
    final_html = convert_mjml_to_html(rendered_mjml)
    return final_html

def design_improvement_agent_wrapper(combined_json: str) -> str:
    data = json.loads(combined_json)
    persona_json = json.dumps(data.get("persona"))
    imagery_json = json.dumps(data.get("imagery"))
    return design_improvement_agent(persona_json, imagery_json)

# ------------------------------------------------------------
# OpenAI Swarm Agent Definitions
# ------------------------------------------------------------
client = Swarm()

intelligence_agent = Agent(
    name="Intelligence Agent",
    instructions="You are the intelligence agent. When given a target profile as JSON, output an enriched JSON profile including news snippets.",
    functions=[gather_intelligence]
)

content_agent = Agent(
    name="Content Agent",
    instructions="You are the content agent. When given an enriched JSON profile, output a JSON with email persona details.",
    functions=[generate_persona]
)

imagery_agent = Agent(
    name="Imagery Agent",
    instructions="You are the imagery agent. When given an enriched JSON profile, output a JSON with imagery data (logo URL, etc.).",
    functions=[generate_imagery]
)

design_agent = Agent(
    name="Design Improvement Agent",
    instructions="You are the design improvement agent. When given a combined JSON (with keys 'persona' and 'imagery'), output the final polished HTML email design.",
    functions=[design_improvement_agent_wrapper]
)

# ------------------------------------------------------------
# Orchestration: Running the Multi-Agent Workflow
# ------------------------------------------------------------
if __name__ == "__main__":
    initial_profile = {
        "name": "Tim Cook",
        "title": "CEO",
        "company": "Apple Inc.",
        "interests": ["technology", "design", "healthcare", "sustainability"],
        "recent_news": "Tim Cook hints new iPhone roadmap shows ‘a lot of innovation’ coming https://9to5mac.com/2025/01/31/tim-cook-hints-new-iphone-roadmap-shows-a-lot-of-innovation-coming/"
    }
    initial_profile_json = json.dumps(initial_profile)
    
    # Run Intelligence Agent.
    result_intel = client.run(agent=intelligence_agent, messages=[{"role": "user", "content": initial_profile_json}])
    enriched_profile = result_intel.messages[-1]["content"]
    print("Enriched Profile:")
    print(enriched_profile)
    
    # Run Content Agent.
    result_content = client.run(agent=content_agent, messages=[{"role": "user", "content": enriched_profile}])
    persona = result_content.messages[-1]["content"]
    # Extract JSON from persona output if needed.
    persona = extract_json_from_output(persona)
    print("\nGenerated Persona:")
    print(persona)
    
    # Run Imagery Agent.
    result_imagery = client.run(agent=imagery_agent, messages=[{"role": "user", "content": enriched_profile}])
    imagery = result_imagery.messages[-1]["content"]
    imagery = extract_json_from_output(imagery)
    print("\nGenerated Imagery:")
    print(imagery)
    
    # Combine persona and imagery into a single JSON.
    combined_input = json.dumps({
        "persona": json.loads(persona),
        "imagery": json.loads(imagery)
    })
    
    # Run Design Improvement Agent.
    result_design = client.run(agent=design_agent, messages=[{"role": "user", "content": combined_input}])
    final_email_html = result_design.messages[-1]["content"]
    print("\nFinal Improved Email HTML:")
    print(final_email_html)
