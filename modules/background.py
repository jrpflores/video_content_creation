import requests
import os
import random
import time
import json
class VideoBackgroundGenerator:
    def __init__(self, type = "video", genre = None, orientation = None, query = ""):
        self.genre = genre
        self.type = type
        self.orientation = orientation
        self.query = query

    def get(self):
        match self.type:
            case "video":
                return self.video()
    def video(self):
        api_key = os.getenv("PEXELS_API_KEY")
        temp_folder = os.getenv("TEMP_FOLDER_PATH")
        timestamp_ms = int(time.time() * 1000)
        os.makedirs(temp_folder, exist_ok=True)
        page = 1  # Random page for variety
        orientation = "" if self.orientation is None else f"&orientation={self.orientation}"
        url = f"https://api.pexels.com/videos/search?query={self.query}&per_page=1&page={page}&size=large{orientation}"  # Get only 1 video
        headers = {"Authorization": api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            video_url = response.json()["videos"][0]["video_files"][0]["link"]
            video_path = f"{temp_folder}/background_video_{timestamp_ms}.mp4"
            with open(video_path, "wb") as f:
                f.write(requests.get(video_url).content)
            return video_path
        raise Exception(f"Error getting video file: {response.text}")