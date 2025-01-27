import re
import tempfile
from dataclasses import dataclass

import stable_whisper
from stable_whisper import result_to_srt_vtt

PATTERN = r'(<font color="(#[a-fA-F0-9]+)">(.*?)</font>)'


@dataclass
class Subtitle:
    content: str
    color: str


def generate_subtitles(video_path: str) -> str:
    print("Loading model...")
    model = stable_whisper.load_model("medium")

    print("Reading file...")
    result = model.transcribe(video_path, fp16=False)
    
    srt_file = tempfile.TemporaryFile(suffix=".srt", delete=False)
    result_to_srt_vtt(result, srt_file.name, word_level=True)
    
    return srt_file.name


def parse_subtitle(text: str) -> list[Subtitle]:
    parsed_data = []

    last_index = 0
    for match in re.finditer(PATTERN, text):
        start, end = match.span()

        if start > last_index:
            plain_text = text[last_index:start]
            if plain_text:
                parsed_data.append(Subtitle(plain_text, "#ffffff"))

        color = match.group(2)
        content = match.group(3)
        parsed_data.append(Subtitle(content, color))

        last_index = end

    if last_index < len(text):
        plain_text = text[last_index:]
        if plain_text:
            parsed_data.append(Subtitle(plain_text, color="#ffffff"))   

    return parsed_data
