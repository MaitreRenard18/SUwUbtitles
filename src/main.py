from subtitles import generate_subtitles
from video import add_subtitles


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
