import google.generativeai as genai
from config import Config
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            return ""
    
    def generate_structured_data(self, prompt: str) -> dict:
        try:
            # Add instruction to return JSON
            json_prompt = f"{prompt}\n\nReturn the response as valid JSON only."
            response = self.model.generate_content(json_prompt)
            
            # Try to parse the response as JSON
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating structured data with Gemini: {e}")
            return {}