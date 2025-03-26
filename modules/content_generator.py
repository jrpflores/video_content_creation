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
        print(provider)
        match provider:
            case "openai":
                self.api_key = os.getenv("OPEN_AI_API_KEY")
            case "deepseek":
                self.api_key = os.getenv("DEEP_SEEK_API_KEY")
            case _:
                self.api_key = None

    def get_content(self, number=None):
        append_text = "and remove quotation marks and return the keyword for background video searching  only one and return in json format with message and keyword"
        prepend_text = "Give me 1 "
        prompts = {
            "facts_trivias": f"{prepend_text} interesting facts or trivias.Ensure uniqueness. Please remove the quotation marks {append_text}",
            "motivational_quotes": f"{prepend_text} Inspirational quote with God. Make it unique {append_text}",
            "pinoy_jokes": f"{prepend_text} hilarious and laughable joke. Ensure it's fresh {append_text}",
            "us_jokes": f"{prepend_text} funny American joke. Make sure it's unique. {append_text}",
            "horror_story": f"{prepend_text}  short horror story in the Philippines in Tagalog. Ensure originality. Remove invalid control characters that causes python to fail  {append_text}"
        }

        prompt = prompts.get(self.content_type, f"Generate something interesting {append_text}.")
        if self.api_provider == "openai":
            return self.ask_openai(prompt)
        if self.api_provider == "deepseek":
            return self.ask_deepseek(prompt)
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
        
    def ask_deepseek(self, prompt):
        if not self.api_key:
            return "DeepSeek API key is missing!"
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek-chat",
                "messages": [
                         {"role": "system", "content": "Generate creative and unique responses."},
                        {"role": "user", "content": prompt}
                        ],
                "temperature": 1.5
            }
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                content = content.strip("```json")
                content = content.strip("```")
                return content
            return f"Error: {response.json()}"
        except Exception as e:
            return f"Error fetching from DeepSeek: {str(e)}"
