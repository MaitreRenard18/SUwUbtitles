import os
import subprocess
import tempfile

import cv2
import numpy as np
import srt
from PIL import Image, ImageDraw, ImageFont

from subtitle_parser import parse_subtitle

FONT = "C:/Windows/Fonts/impact.ttf"
FONT_SIZE = 32
TEXT_POSITION = (50, 50)

OUTPUT_PATH = "out/result.mp4"


def put_custom_text(frame, text, font_path, font_size):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    draw = ImageDraw.Draw(pil_image)
    W, H = pil_image.size
    
    font = ImageFont.truetype(font_path, font_size)

    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    centered_position = ((W-w)/2, (H-h)/2)
    x_offset = 0
    
    for part in parse_subtitle(text):
        position = (centered_position[0] + x_offset, centered_position[1]) 
        draw.text(position, part.content, font=font, fill=part.color)
        
        _, _, part_width, _ = draw.textbbox((0, 0), part.content, font=font)
        x_offset += part_width

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def add_subtitles(input_video: str, srt_file: str):
    cap = cv2.VideoCapture(input_video)
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    
    no_audio_video = tempfile.TemporaryFile(suffix=".mp4", delete=False)
    out = cv2.VideoWriter(no_audio_video.name, fourcc, fps, (frame_width, frame_height))

    with open(srt_file, mode="r", encoding="utf-8") as file:
        subtitles = srt.parse(file.read().replace("#00ff00", "#ff0000")) # Load subtitles and replace green by red

    frame_index = 0
    current_subtitle = next(subtitles, None)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        time_code = frame_index / fps
        if current_subtitle:   
            if time_code >= current_subtitle.end.total_seconds():
                current_subtitle = next(subtitles, None)
            
            if current_subtitle and current_subtitle.start.total_seconds() <= time_code <= current_subtitle.end.total_seconds():
                frame = put_custom_text(frame, current_subtitle.content.capitalize(), FONT, FONT_SIZE)
            

        out.write(frame)
        frame_index += 1

    cap.release()
    out.release()

    add_audio(input_video, no_audio_video.name, OUTPUT_PATH)
    
    no_audio_video.close()
    os.remove(no_audio_video.name)


def add_audio(input_video: str, input_video_no_audio: str, output_video: str):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_video_no_audio,
        "-i", input_video,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0", 
        output_video
    ]
    subprocess.run(command)
    print("Vidéo finale avec sous-titres et audio créée :", output_video)
    
if __name__ == "__main__":
    from time import time
    
    t0 = time()
    add_subtitles("in/Undertale.mp4", "out/sub.srt")
    print(f"Generated in {time() - t0}")
