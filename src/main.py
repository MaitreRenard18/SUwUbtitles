import tempfile

import stable_whisper
from stable_whisper import result_to_srt_vtt

from video import add_subtitles


def generate_subtitles(video_path: str) -> str:
    print("Loading model...")
    model = stable_whisper.load_model("medium").to("cuda")

    print("Reading file...")
    result = model.transcribe(video_path, fp16=False)
    
    srt_file = tempfile.TemporaryFile(suffix=".srt", delete=False)
    result_to_srt_vtt(result, srt_file.name, word_level=True)
    
    return srt_file.name


def generate_video(video_path: str) -> None:
    srt_file_path = generate_subtitles(video_path)
    add_subtitles(video_path, srt_file_path)


if __name__ == "__main__":
    import tkinter as tk
    from time import time
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(initialdir="./in")

    t0 = time()
    generate_video(file_path)
    print(f"Generated in {time() - t0}")
