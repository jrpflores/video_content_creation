from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, concatenate_videoclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn

import os
import time
import textwrap
import cv2
import numpy as np
import subprocess
import whisper
class VideoProcessor:
    def __init__(self, text=None, video_path = None, voiceover_path = None, content_size = "normal", max_char_per_chunk = 500):
        self.video_path = video_path
        self.voiceover_path = voiceover_path
        self.content_size = content_size #normal and reels
        self.text = text
        self.max_char_per_chunk = max_char_per_chunk
    
    def set_size(self, size):
        self.content_size = size
    def blur_frame(self,frame):
        return cv2.GaussianBlur(frame, (25, 25), 5)
    def create(self):
       

        # Get system fonts using fc-list
        # fonts = subprocess.check_output(["fc-list", ":family"], universal_newlines=True)

        # print(fonts)

        # exit()
        if not self.video_path or not os.path.exists(self.video_path):
            raise FileNotFoundError("Video file not found.")
        
        # Load video
        temp_folder = os.getenv("UPLOAD_PATH", "/tmp")
        timestamp_ms = int(time.time() * 1000)
        video = VideoFileClip(self.video_path) 
        if self.content_size == "reels":
            output_path = f"{temp_folder}/reels_final_{timestamp_ms}.mp4"
            final_width, final_height = 1080, 1920
        else:
            output_path = f"{temp_folder}/final_result_{timestamp_ms}.mp4"
            final_width, final_height = video.w, video.h
        
        duration = video.duration
        voiceover = None
        if self.voiceover_path and os.path.exists(self.voiceover_path):
            voiceover = AudioFileClip(self.voiceover_path)
            duration = voiceover.duration 
            looped_video = None
            if voiceover.duration < video.duration:
                video = video.subclipped(0, voiceover.duration)
            else: 
                num_loops = int(voiceover.duration // video.duration) + 1
                looped_video = concatenate_videoclips([video] * num_loops)
                video = looped_video.subclipped(0, voiceover.duration)

        video = video.resized(height=final_height, width=final_width)
        video = video.with_position("center")
        # video = video.transform(lambda get_frame, t: self.blur_frame(get_frame(t)))

        background = ColorClip(size=(final_width, final_height), color=(0, 0, 0)).with_duration(duration)

        max_chars_per_chunk = self.max_char_per_chunk
        text_chunks = textwrap.wrap(self.text or "", max_chars_per_chunk)
        num_chunks = len(text_chunks)
        chunk_duration = duration / max(num_chunks, 1)

        if not self.voiceover_path or not os.path.exists(self.voiceover_path):
            chunk_duration

        # Create text clips that appear sequentially
        txt_clips = []
        text_length = max_chars_per_chunk if num_chunks > 1 else len(self.text)
        font_size = self.font_size_identifier(text_length)
        for i, chunk in enumerate(text_chunks):
            txt_clip = TextClip(
                text=chunk, 
                size=(int(final_width * 0.6), None),  
                color="white", 
                font="Futura",
                method="caption",
                stroke_color="black",
                stroke_width=2,
                font_size=font_size,
                text_align="center"
            ).with_duration(chunk_duration).with_start(i * chunk_duration).with_position(("center",int(final_height*0.22)))
            # Get text size dynamically
            txt_w, txt_h = txt_clip.size  
            # Create background box for text
            bg_clip = ColorClip(
                size=(int(final_width * 0.65), int(txt_h)+(int(txt_h*.1))),  # Padding around text
                color=(0, 0, 0)  # Black background
            ).with_duration(chunk_duration).with_start(i * chunk_duration).with_position(("center",int(final_height*0.2))).with_opacity(0.2)
            txt_clips.append(bg_clip)
            txt_clips.append(txt_clip)
            
        # timestamps = self.get_word_timestamps(self.voiceover_path)
        # text_chunks = self.chunk_text_by_timestamps(self.text, timestamps, max_chars_per_chunk)
        # txt_clips = self.create_text_clips(text_chunks, final_width, final_height, font_size)

        final = CompositeVideoClip([background, video] + txt_clips)
        if voiceover: 
            final = final.with_audio(voiceover)
        # Export final video
        final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", audio=True)
        final.close()
        print(f"✅ Video saved as {output_path}")
        return output_path
    
    def font_size_identifier(self,text_length):
        if(text_length <= 50):
            return 100
        if(text_length < 100):
            return 90
        if text_length < 200:
            return 65
        if text_length < 300:
            return 45
        return 40
    
    def chunk_text_by_timestamps(self, text, timestamps, max_chars_per_chunk):
        words = text.split()
        grouped_chunks = []
        chunk = []
        chunk_start = None

        for word, start, end in timestamps:
            if chunk_start is None:
                chunk_start = start

            chunk.append(word)

            if len(" ".join(chunk)) >= max_chars_per_chunk:
                grouped_chunks.append((" ".join(chunk), chunk_start, end))
                chunk = []
                chunk_start = None

        if chunk:  # Last remaining chunk
            grouped_chunks.append((" ".join(chunk), chunk_start, timestamps[-1][2]))

        return grouped_chunks
    
    def create_text_clip(self, text_chunks, final_width, final_height, fontsize):
        txt_clips = []
        for chunk, start, end in text_chunks:
            chunk_duration = end - start
            txt_clip = TextClip(
                text=chunk, 
                size=(int(final_width * 0.6), None),  
                color="white", 
                font="Futura",
                method="caption",
                stroke_color="black",
                stroke_width=2,
                font_size=fontsize,
                text_align="center"
            ).with_duration(chunk_duration).with_start(start).with_position(("center",int(final_height*0.22)))
            # Get text size dynamically
            txt_w, txt_h = txt_clip.size  
            # Create background box for text
            bg_clip = ColorClip(
                size=(int(final_width * 0.65), int(txt_h)+(int(txt_h*.2))),  # Padding around text
                color=(0, 0, 0)  # Black background
            ).with_duration(chunk_duration).with_start(i * chunk_duration).with_position(("center",int(final_height*0.2))).with_opacity(0.2)
            txt_clips.append(bg_clip)
            txt_clips.append(txt_clip)
        
        return txt_clips
    
    def get_word_timestamps(self, audio_path):
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)

        timestamps = []
        for segment in result["segments"]:
            for word in segment["words"]:
                timestamps.append((word["text"], word["start"], word["end"]))  # (word, start_time, end_time)
        
        return timestamps