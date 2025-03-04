import openai
import requests
import os
import time
import random
class ContentGenerator:
    def __init__(self, content_type="facts_trivias", api_provider="openai"):
        self.content_type = content_type.lower()
        self.api_provider = api_provider.lower()
        self.load_key(api_provider.lower())
        
    def load_key(self, provider):
        match provider:
            case "openai":
                self.api_key = os.getenv("OPEN_AI_API_KEY")
            case _:
                self.api_key = None

    def get_content(self, number=None):
        prompts = {
            "facts_trivias": "Give me an interesting fact or trivia. Ensure uniqueness.",
            "motivational_quotes": "Give me a realistic motivational quote. Make it unique and at most 50 characters.",
            "pinoy_jokes": "Give me a funny Pinoy joke in Tagalog. Ensure it's fresh.",
            "us_jokes": "Give me a funny American joke. Make sure it's unique.",
            "horror_story": "Give me a short horror story in the Philippines in Tagalog. Ensure originality."
        }

        prompt = prompts.get(self.content_type, "Generate something interesting.")
        
        if self.api_provider == "openai":
            return self.ask_openai(prompt)
        elif self.api_provider == "gemini":
            return self.ask_gemini(prompt)
        else:
            return "Sorry, API provider not supported."

    def ask_openai(self, prompt):
        if not self.api_key:
            return "OpenAI API key is missing!"
        
        try:
            openai.api_key = self.api_key
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate creative and unique responses."},
                    {"role": "user", "content": f"{prompt}"}
                ],
                temperature=0.9  # Increase randomness
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error fetching from OpenAI: {str(e)}"

    def ask_gemini(self, prompt):
        if not self.api_key:
            return "Gemini API key is missing!"
        
        try:
            url = "https://api.gemini.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {"model": "gemini-1", "messages": [{"role": "user", "content": prompt}], "max_tokens": 50}
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            return f"Error: {response.json()}"
        except Exception as e:
            return f"Error fetching from Gemini: {str(e)}"
