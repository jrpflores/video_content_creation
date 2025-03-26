import requests
import os
import time
import json
import base64
class VoiceoverGenerator:
    def __init__(self, text, provider = "google", language_code = "en-US"):
        self.provider = provider
        self.text = text
        self.language_code = language_code
        self.model_id = None
        self.load_default()
    def load_default(self):
        match self.provider:
            case "google":
                self.model_id = "fil-PH-Standard-C" if self.language_code == "fil-PH" else "en-US-Standard-C"
            case "elevenlabs":
                self.model_id = "eleven_multilingual_v2" if self.language_code == "fil-PH" else "eleven_flash_v2"

    def get_voiceover(self):
        if self.provider == "elevenlabs":
            return self.elevenlabs()
        elif self.provider == "google":
            return self.google_tts()
        else:
            raise ValueError("Unsupported provider. Use 'google' or 'elevenlabs'.")
    
    def elevenlabs(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        temp_folder = os.getenv("TEMP_FOLDER_PATH")
        timestamp_ms = int(time.time() * 1000)
        os.makedirs(temp_folder, exist_ok=True)
        path = f"{temp_folder}/voiceover_{timestamp_ms}.mp3"
        url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128"
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": self.text,
            "model_id": self.model_id #eleven_multilingual_v2
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return path
        raise Exception(f"Error generating an audio: {response.text}")
    
    def google_tts(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing Google API Key. Set 'GOOGLE_API_KEY' in environment variables.")

        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"

        payload = {
            "input": {"text": self.text},
            "voice": {
                "languageCode": self.language_code,
                "name": self.model_id
            },
            "audioConfig": {
                "audioEncoding": "MP3"
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            audio_content = response.json().get("audioContent")
            if audio_content:
                temp_folder = os.getenv("TEMP_FOLDER_PATH")
                os.makedirs(temp_folder, exist_ok=True)
                timestamp_ms = int(time.time() * 1000)
                path = f"{temp_folder}/voiceover_{timestamp_ms}.mp3"
                with open(path, "wb") as f:
                    f.write(base64.b64decode(audio_content))
                return path
        else:
            raise Exception(f"Google TTS API Error: {response.text}")