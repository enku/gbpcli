"""notes subcommand for gbpcli"""
import argparse
import os
import subprocess
import sys
import tempfile
from typing import Optional

from gbpcli import GBP, Build
from gbpcli.queries import create_note


def get_editor():
    """Return the user's editor preference.

    Does this by inpsecting first the VISUAL environment variable then the EDITOR
    environment variable.

    If both of these are not defined or empty string then return `None`.
    """
    if editor := os.getenv("VISUAL", None):
        return editor

    if editor := os.getenv("EDITOR", None):
        return editor

    return None


def open_editor(editor: str, text: Optional[str]) -> str:
    """Open the given `editor` and return the text after the editor exits.

    The optional `text` argument is the existing text to be edited. If not given then
    the editor will open with an empty buffer.

    If the editor exits with a non-zero status then raise `EnvironmentError`.
    """
    with tempfile.NamedTemporaryFile("w+") as note_file:
        if text:
            note_file.write(text)
            note_file.flush()
        proc = subprocess.run([editor, note_file.name], check=False)

        if proc.returncode == 0:
            note_file.seek(0)
            return note_file.read()

    raise EnvironmentError("Editor failed")


def get_note(existing_note: Optional[str]) -> str:
    """Get a note either from standard input or editor"""
    if sys.stdout.isatty() and (editor := get_editor()):
        note = open_editor(editor, existing_note)
    else:
        note = sys.stdin.read()

    return note


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """handler"""
    build = Build(args.machine, args.number)
    existing = gbp.get_build_info(build)

    if not existing or not existing.info:
        print("Build not found", file=sys.stderr)
        return 1

    if args.delete:
        note = None
    else:
        try:
            note = get_note(existing.info.note)
        except EnvironmentError:
            return 1

    gbp.check(create_note, {"name": args.machine, "number": args.number, "note": note})

    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("--delete", "-d", action="store_true", default=False)
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
