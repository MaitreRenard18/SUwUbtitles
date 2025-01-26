import tempfile

import srt
import stable_whisper
from moviepy import CompositeVideoClip, TextClip, VideoFileClip
from stable_whisper import result_to_srt_vtt


def generate_subtitles(video_path: str) -> str:
    print("Loading model...")
    model = stable_whisper.load_model("medium").to("cuda")

    print("Reading file...")
    result = model.transcribe(video_path, fp16=False)
    
    srt_file = tempfile.TemporaryFile(suffix=".srt", delete=False)
    result_to_srt_vtt(result, srt_file.name, word_level=False)
    
    return srt_file.name


def generate_video(video_path: str) -> None:
    clip = VideoFileClip(video_path)
    srt_file_path = generate_subtitles(video_path)
    texts = []

    srt_content = ""
    with open(srt_file_path, 'r') as f:
        srt_content = f.read()
    
    for subtitle in srt.parse(srt_content):
        txt_clip = TextClip(
            font="C:/Windows/Fonts/impact.ttf",
            text=subtitle.content.capitalize(),
            size =(clip.size[0] // 3, clip.size[1] // 3),
            method="caption",
            color='white',
            text_align="center",
            vertical_align="center",
            horizontal_align="center",
        ).with_start(subtitle.start.total_seconds()).with_end(subtitle.end.total_seconds()).with_position('center')
        
        texts.append(txt_clip)

    # Overlay the text clip on the first video clip
    final_video = CompositeVideoClip([clip, *texts])
    final_video.write_videofile("out/result.mp4")


result = generate_video("in/Undertale.mp4")
