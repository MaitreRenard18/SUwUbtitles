import os
import re
from dataclasses import dataclass
from datetime import timedelta
from tempfile import TemporaryFile
from typing import Generator

import srt
import stable_whisper
from stable_whisper import result_to_srt_vtt

PATTERN = r'(<font color="(#[a-fA-F0-9]+)">(.*?)</font>)'


@dataclass
class SubtitleChunk:
    content: str
    color: str


class RichSubtitle(srt.Subtitle):
    def __init__(self, index: int, start: timedelta, end: timedelta, chunks: list[SubtitleChunk], proprietary: str = ""):
        super().__init__(index, start, end, ''.join(map(lambda x: x.content, chunks)), proprietary)    
        self.chunks = chunks


class SubtitleGenerator():
    _model = None

    @staticmethod
    def get_model():
        if SubtitleGenerator._model is None:
            print("Loading model")
            SubtitleGenerator._model = stable_whisper.load_model("medium")
            
        return SubtitleGenerator._model
    
    @staticmethod
    def generate_str(video: str | bytes, word_level=True) -> str:
        if isinstance(video, str):
            result = SubtitleGenerator.get_model().transcribe(video, fp16=False)
        
        else:
            with TemporaryFile(mode="bw+", suffix=".mp4", delete=False) as temp:
                temp.write(video)
                result = SubtitleGenerator.get_model().transcribe(temp.name, fp16=False)
        
            os.remove(temp.name)
        
        return result_to_srt_vtt(result, word_level=word_level)

    @staticmethod
    def parse(text: str) -> Generator[RichSubtitle, None, None]:
        for i, subtitle in enumerate(srt.parse(text)):
            chunks = []
            
            last_index = 0
            for match in re.finditer(PATTERN, subtitle.content):
                start, end = match.span()

                if start > last_index:
                    plain_text = subtitle.content[last_index:start]
                    if plain_text:
                        chunks.append(SubtitleChunk(plain_text, "#ffffff"))

                color = match.group(2)
                content = match.group(3)
                chunks.append(SubtitleChunk(content, color))

                last_index = end

            if last_index < len(subtitle.content):
                plain_text = subtitle.content[last_index:]
                if plain_text:
                    chunks.append(SubtitleChunk(plain_text, color="#ffffff"))
            
            yield RichSubtitle(i, subtitle.start, subtitle.end, chunks, subtitle.proprietary) 
