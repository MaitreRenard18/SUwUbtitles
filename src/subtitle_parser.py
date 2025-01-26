import re
from dataclasses import dataclass

PATTERN = r'(<font color="(#[a-fA-F0-9]+)">(.*?)</font>)'


@dataclass
class Subtitle:
    content: str
    color: str


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

if __name__ == "__main__":
    print(parse_subtitle('Here <font color="#00ff00">we</font> are again,'))