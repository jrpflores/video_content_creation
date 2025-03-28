from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import random
import json
import traceback
import time
import re
import string
# Load the .env file
load_dotenv()

from modules.content_generator import ContentGenerator
from modules.voiceover_generator import VoiceoverGenerator
from modules.background import VideoBackgroundGenerator
from modules.video_creator import VideoProcessor
from modules.uploads import GoogleDriveUploader
from modules.mailer import GmailOAuthSender

root_folder = os.getenv("ROOT_FOLDER_PATH", "")
def process_gdrive(file_path, file_name):
    credentials_file = f"{root_folder}credentials.json"
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


def generate(content_type="facts_trivias", content_size="reels", max_retries=3):
    now = datetime.now()
    # Format it as "YYYY-MM-DD-HH-MM"
    formatted_time = now.strftime("%Y-%m-%d-%H-%M")
    ai_provider = os.getenv('AI_PROVIDER')
    if len(sys.argv) > 1 and sys.argv[1]:
        content_type = sys.argv[1]

    retries = 0
    status = False
    while retries < max_retries:
        temp_files = []
        try:
            print(f"Generating content for {content_type}...")
            #step 1: get the content
            text_content_ai = ContentGenerator(content_type, ai_provider).get_content()
            print(text_content_ai)
            data = json.loads(text_content_ai)
            text_content = data['message'].strip()
            keyword = data['keyword']


            #step 2: generate voice over
            content_types_use_multilingual = ["horror_story"]
            no_voice_over = ["motivational_quotes"]
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
                "motivational_quotes": random.choice(["nature", "ocean", "city", "mountains", "forest", "sky", "waterfall"]),
                "pinoy_jokes": random.choice(["philippines", "laugh", "comedy", "happy", "people laughin"]),
                "us_jokes": random.choice(["united states of america", "laugh", "comedy", "happy"]),
                "horror_story": random.choice(["horror", "scary", "cementery", "haunted house"])
            }
            # if content_type in ["horror_story"]:
            #     keyword =background_keywords.get(content_type, "")
            # keyword =background_keywords.get(content_type, "")
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
             # Cleanup temp files
            status = True
            break  # Exit loop if successful

        except Exception as e:
            retries += 1
            print(f"Error on attempt {retries}: {e}")
            print("Traceback:", traceback.format_exc())
            if retries < max_retries:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Max retries reached. Process failed.")
        finally:
            for file in temp_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted file: {file}")
    return status
        
def main():
    content_types = ["facts_trivias", "motivational_quotes", "pinoy_jokes", "horror_story"] 
    # content_types = ["horror_story"]
    statuses = []
    for _ in range(5):
        for content_type in content_types:
            status = generate(content_type)
            statuses.append(status)
    
    all_false = not any(statuses)
    if all_false:
        print("all processed failed")
        exit()

    #email after processing
    current_day = datetime.now().strftime("%A")
    gmail_sender = GmailOAuthSender(f"{root_folder}credentials.oauth.json")
    gmail_sender.send_email(
        sender_email=os.getenv('EMAIL_SENDER'),
        recipient_email=os.getenv('EMAIL_RECEIPIENTS'),
        subject=f"New Content Created in {current_day} folder",
        body=f"New Content Created in {current_day} folder"
    )
if __name__ == "__main__":
    main()