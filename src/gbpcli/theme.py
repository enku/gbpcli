"""Utilities for getting/setting the color theme"""
from rich.theme import Theme

DEFAULT_THEME = {
    "box": "default",
    "build_id": "bold",
    "header": "bold",
    "keep": "yellow",
    "machine": "blue",
    "mymachine": "default",
    "note": "default",
    "note_flag": "blue",
    "package": "magenta",
    "published": "bold green",
    "tag": "yellow",
    "timestamp": "default",
    "yes": "green",
    "no": "default",
    "added": "green",
    "removed": "red",
}


def get_theme_from_string(string: str) -> Theme:
    """Given the text string return a rich Theme

    String is expected to be a colon-delimited (":") set of name=value pairs. So for
    example:

        "build_id=bold:header=bold:keep=yellow:machine=blue"

    Values are stripped of whitespace. If the fields cannot be parsed a `ValueError` is
    raised.  Empty names/values are ignored.
    """
    colormap = DEFAULT_THEME.copy()

    for assignment in string.split(":"):
        if not assignment:
            continue

        name, value = parse_assignment(assignment)

        if not name or not value:
            continue

        colormap[name] = value

    return Theme(colormap)


def parse_assignment(assignment: str) -> tuple[str, str]:
    """parse 'name=value' string into (name, value)"""
    try:
        name, value = assignment.split("=")
    except ValueError:
        raise ValueError(f"Invalid theme assignment: {assignment!r}") from None

    return name.strip(), value.strip()
