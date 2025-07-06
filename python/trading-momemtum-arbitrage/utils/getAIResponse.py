import os, json, re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Function to send a prompt and get response
def query_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def extract_json_from_text(text: str) -> dict:
    """
    Clean and parse JSON from Gemini-style Markdown response.
    """
    # Remove Markdown-style code block fences (```json ... ```)
    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")