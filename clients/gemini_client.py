from google import genai
from core.config import settings

class GeminiClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_content(self, prompt):
        
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text
    
    def recommend_task(self, prompt):
        
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text

        