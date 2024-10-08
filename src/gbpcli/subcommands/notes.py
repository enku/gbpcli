"""notes subcommand for gbpcli"""

import argparse
import os
import subprocess
import sys
import tempfile

from gbpcli import GBP, render, utils
from gbpcli.subcommands import make_searchable
from gbpcli.types import Console, SearchField

HELP = """notes subcommand for gbpcli"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show, search, and edit build notes"""
    if args.search:
        return search_notes(gbp, args.machine, args.number, console)

    build = utils.resolve_build_id(args.machine, args.number, gbp)
    existing = gbp.get_build_info(build)

    if not (existing and existing.info):
        console.err.print("Build not found")
        return 1

    if args.delete:
        note = None
    else:
        try:
            note = get_note(existing.info.note)
        except EnvironmentError:
            return 1

    gbp.create_note(build, note)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("--delete", "-d", action="store_true", default=False)
    make_searchable(parser)


def search_notes(gbp: GBP, machine: str, key: str, console: Console) -> int:
    """--search handler for the notes subcommand"""
    if not (builds := gbp.search(machine, SearchField.notes, key)):
        console.err.print("No matches found")
        return 1

    sep = ""
    for build in builds:
        console.out.print(sep, end="")
        console.out.print(render.build_to_str(build), end="")
        sep = "\n"

    return 0


def get_note(existing_note: str | None) -> str:
    """Get a note either from standard input or editor"""
    return (
        open_editor(editor, existing_note)
        if sys.stdin.isatty() and (editor := get_editor())
        else sys.stdin.read()
    )


def get_editor() -> str | None:
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


def open_editor(editor: str, text: str | None) -> str:
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

        if not proc.returncode:
            note_file.seek(0)
            return note_file.read()

    raise EnvironmentError("Editor failed")
