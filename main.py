from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import random
# Load the .env file
load_dotenv()

from modules.content_generator import ContentGenerator
from modules.voiceover_generator import VoiceoverGenerator
from modules.background import VideoBackgroundGenerator
from modules.video_creator import VideoProcessor
from modules.uploads import GoogleDriveUploader

def process_gdrive(file_path, file_name):
    credentials_file = "credentials.json"
    uploader = GoogleDriveUploader(credentials_file)
    current_day = datetime.now().strftime("%A")
    folder_ids_by_day = {
        "Monday": "13aVyz0TbsLimnmg--Q0FgM4PPs-DI-5u",
        "Tuesday": "1HAZje7n2uJn5yTX2ig57gLsklR1REEFk",
        "Wednesday": "1pjk-HqeDZGFM6p-W-j6_UqrVT6dzvVSN",
        "Thursday": "1lvSGCQ-A4fa0J9i4rwim9TOF65ggldq4",
        "Friday": "1FtYrS2xgUNfZ58rQbySRp7V2h3WkpA3x",
        "Saturday": "1l31oEfrsxU0QVBdYI02mnyPQmwqucvJE",
        "Sunday": "1YHlQZmCrah5Da3d0oG3cMfOqjazyB7gM"
    }
    folder_id =folder_ids_by_day.get(current_day, "")

    if folder_id == "":
        raise Exception("No folder id")
    
    uploaded_file_id = uploader.upload_file(file_path, file_name, folder_id)


def main():
    now = datetime.now()
    # Format it as "YYYY-MM-DD-HH-MM"
    formatted_time = now.strftime("%Y-%m-%d-%H-%M")
    content_type = "facts_trivias"
    content_size = "reels"
    ai_provider = os.getenv('AI_PROVIDER')
    if len(sys.argv) > 1 and sys.argv[1]:
        content_type = sys.argv[1]

    temp_files = []

    try:
        #step 1: get the content
        text_content = ContentGenerator(content_type, ai_provider).get_content()


        #step 2: generate voice over
        content_types_use_multilingual = ["pinoy_jokes", "horror_story"]
        no_voice_over = ["facts_trivias", "motivational_quotes"]
        voice_model ="en-US"
        if content_type in content_types_use_multilingual:
            voice_model = "fil-PH"
        
        voice_over_file = None
        if content_type not in no_voice_over:
            voice_over_file = VoiceoverGenerator(text_content, language_code=voice_model).get_voiceover()
            temp_files.append(voice_over_file)


        #step 3: get backgroud video 
        background_keywords = {
            "facts_trivias": random.choice(["nature", "ocean", "city", "mountains", "forest", "sky", "waterfall", "bulb", "light bulb"]),
            "motivational_quotes": random.choice(["nature", "ocean", "city", "mountains", "forest", "sky", "waterfall", "inspired", "motivational"]),
            "pinoy_jokes": random.choice(["philippines", "laugh", "comedy", "happy", "people laughin"]),
            "us_jokes": random.choice(["united states of america", "laugh", "comedy", "happy"]),
            "horror_story": random.choice(["horror", "scary", "cementery", "haunted house"])
        }
        keyword =background_keywords.get(content_type, "")
        orientation = "portrait" if content_size == "reels" else "landscape"
        background_video = VideoBackgroundGenerator(orientation=orientation, query=keyword).get()
        temp_files.append(background_video)

        #step 4: TODO: get background instrumental

        #step 5: process resources
        output_file = VideoProcessor(text_content, 
                                    voiceover_path=voice_over_file, 
                                    video_path=background_video,
                                    content_size=content_size,).create()

        #step 6: upload to gdrive
        process_gdrive(output_file, f"{content_size}_{content_type}_{formatted_time}.mp4")
        #temp_files.append(output_file)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Deleted file: {file}")
        

if __name__ == "__main__":
    main()