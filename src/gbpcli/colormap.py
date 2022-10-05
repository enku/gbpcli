"""Style/colors for gbpcli"""
from typing import Dict

ColorMap = Dict[str, str]

DEFAULT: ColorMap = {
    "build_id": "bold",
    "header": "bold",
    "keep": "yellow",
    "machine": "blue",
    "note": "#ffffff italic",
    "note_flag": "blue",
    "package": "magenta",
    "published": "bold green",
    "tag": "yellow",
    "timestamp": "default",
    "yes": "green",
    "no": "default",
}


def get_colormap_from_string(text: str) -> ColorMap:
    colormap = DEFAULT.copy()

    for assignment in text.split(":"):
        name, value = assignment.split("=")

        if name in colormap:
            colormap[name] = value.strip()

    return colormap
