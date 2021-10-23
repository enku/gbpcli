"""Tests for the notes subcommand"""
# pylint: disable=missing-function-docstring
import os
import subprocess
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.notes import handler as create_note

from . import TestCase, mock_print


class NotesTestCase(TestCase):
    """notes tests"""

    maxDiff = None

    def setUp(self):
        super().setUp()

        self.args = Namespace()
        self.args.machine = "lighthouse"
        self.args.number = 3109
        self.args.delete = False
        self.make_response("show.json")
        self.make_response("create_note.json")

    def test_create_with_editor(self):
        editor = fake_editor("Hello world\n")

        with mock.patch(
            "gbpcli.subcommands.notes.sys.stdout.isatty", return_value=True
        ):
            with mock.patch(
                "gbpcli.subcommands.notes.subprocess.run", wraps=editor
            ) as run:
                with mock.patch.dict(os.environ, {"EDITOR": "foo"}, clear=True):
                    status = create_note(self.args, self.gbp)

        self.assertEqual(status, 0)
        self.assert_graphql(
            queries.create_note,
            name="lighthouse",
            index=1,
            number=3109,
            note="Hello world\n",
        )
        run.assert_called_once()
        call_args = run.call_args
        self.assertEqual(call_args[0][0][0], "foo")

    def test_create_with_editor_but_editor_fails_does_not_create_note(self):
        editor = fake_editor("Hello world\n", returncode=1)

        with mock.patch(
            "gbpcli.subcommands.notes.sys.stdout.isatty", return_value=True
        ):
            with mock.patch(
                "gbpcli.subcommands.notes.subprocess.run", wraps=editor
            ) as run:
                with mock.patch.dict(os.environ, {"VISUAL": "foo"}, clear=True):
                    status = create_note(self.args, self.gbp)

        self.assertEqual(status, 1)
        self.assertEqual(self.gbp.session.post.call_count, 1)
        run.assert_called_once()
        call_args = run.call_args
        self.assertEqual(call_args[0][0][0], "foo")

    def test_when_isatty_but_no_editor_reads_from_stdin(self):
        with mock.patch(
            "gbpcli.subcommands.notes.sys.stdout.isatty", return_value=True
        ):
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch(
                    "gbpcli.subcommands.notes.sys.stdin.read",
                    return_value="Hello world\n",
                ):
                    status = create_note(self.args, self.gbp)

        self.assertEqual(status, 0)
        self.assert_graphql(
            queries.create_note,
            name="lighthouse",
            index=1,
            number=3109,
            note="Hello world\n",
        )

    def test_delete_deletes_note(self):
        self.args.delete = True
        create_note(self.args, self.gbp)

        self.assert_graphql(
            queries.create_note, index=1, name="lighthouse", number=3109, note=None
        )

    def test_create_with_no_tty(self):
        args = Namespace()
        args.machine = "lighthouse"
        args.number = 3109
        args.delete = False
        self.make_response("show.json")
        self.make_response("create_note.json")

        with mock.patch(
            "gbpcli.subcommands.notes.sys.stdout.isatty", return_value=False
        ):
            with mock.patch(
                "gbpcli.subcommands.notes.sys.stdin.read", return_value="Hello world\n"
            ):
                create_note(args, self.gbp)

        self.assert_graphql(
            queries.create_note,
            name="lighthouse",
            index=1,
            number=3109,
            note="Hello world\n",
        )

    @mock_print("gbpcli.subcommands.notes")
    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        self.make_response(None)
        self.make_response({"data": {"build": None}})

        status = create_note(self.args, self.gbp)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Build not found\n")


def fake_editor(text, returncode=0):
    def edit(args, check=False):
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, args)

        with open(args[1], "w", encoding="utf-8") as note_file:
            note_file.write(text)

        return mock.Mock(returncode=returncode)

    return edit
