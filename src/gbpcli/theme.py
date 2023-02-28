"""Utilities for getting/setting the color theme"""
ColorMap = dict[str, str]
DEFAULT_THEME: ColorMap = {
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


def get_colormap_from_string(string: str) -> ColorMap:
    """Given the text sring return a gbp ColorMap

    String is expected to be a colon-delimited (":") set of name=value pairs. So for
    example:

        "build_id=bold:header=bold:keep=yellow:machine=blue"

    Values are stripped of whitespace. If the fields cannot be parsed a `ValueError` is
    raised.  Empty names/values are ignored as are unrecognized names.
    """
    colormap = DEFAULT_THEME.copy()
    error = ValueError(f"Invalid color map: {string!r}")

    if not string:
        return colormap

    for assignment in string.split(":"):
        if not assignment:
            continue
        try:
            name, value = assignment.split("=")
        except ValueError:
            raise error from None

        name = name.strip()
        name = name.strip()

        if not name or not value:
            continue

        if name in colormap:
            colormap[name] = value.strip()

    return colormap
