"""Tests for the notes subcommand"""
# pylint: disable=missing-function-docstring
import os
import subprocess
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.notes import handler as create_note

from . import LOCAL_TIMEZONE, TestCase, mock_print

MODULE = "gbpcli.subcommands.notes"
NOTE = "Hello world\n"


@mock.patch("gbpcli.utils.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class NotesTestCase(TestCase):
    """notes tests"""

    maxDiff = None

    def setUp(self):
        super().setUp()

        self.args = Namespace(
            machine="lighthouse", number="3109", delete=False, search=False
        )
        self.make_response("status.json")
        self.make_response("create_note.json")

    def assert_create_note(self, machine="lighthouse", number="3109", note=NOTE):
        """Assert that the note was created by a GraphQL request"""
        self.assert_graphql(queries.build, index=0, id=f"{machine}.{number}")
        self.assert_graphql(
            queries.create_note, id=f"{machine}.{number}", index=1, note=note
        )

    def test_create_with_editor(self):
        editor = fake_editor()

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, {"EDITOR": "foo"}, clear=True):
                    status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_create_note()
        run.assert_called_once()
        call_args = run.call_args
        self.assertEqual(call_args[0][0][0], "foo")

    def test_create_with_editor_but_editor_fails_does_not_create_note(self):
        editor = fake_editor(returncode=1)

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, {"VISUAL": "foo"}, clear=True):
                    status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(self.gbp.session.post.call_count, 1)
        run.assert_called_once()
        call_args = run.call_args
        self.assertEqual(call_args[0][0][0], "foo")

    def test_when_isatty_but_no_editor_reads_from_stdin(self):
        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                    status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_create_note()

    def test_delete_deletes_note(self):
        self.args.delete = True
        create_note(self.args, self.gbp, self.console)

        self.assert_create_note(note=None)

    def test_create_with_no_tty(self):
        self.make_response("status.json")
        self.make_response("create_note.json")

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=False):
            with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                create_note(self.args, self.gbp, self.console)

        self.assert_create_note()

    @mock_print(MODULE)
    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        self.make_response(None)
        self.make_response({"data": {"build": None}})

        status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Build not found\n")

    @mock_print("gbpcli.utils")
    def test_should_print_error_when_invalid_number_given(self, print_mock):
        self.args.number = "foo"

        with self.assertRaises(SystemExit):
            create_note(self.args, self.gbp, self.console)

        self.assertEqual(print_mock.stderr.getvalue(), "Invalid build ID: foo\n")

    def test_search_notes(self):
        self.args.search = True
        self.args.number = "foo"
        self.make_response(None)
        self.make_response("search_notes.json")

        status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(queries.search_notes, machine="lighthouse", key="foo")
        self.assertEqual(self.console.getvalue(), EXPECTED_SEARCH_OUTPUT)

    @mock_print(MODULE)
    def test_search_no_matches_found(self, print_mock):
        self.args.search = True
        self.args.number = "python"
        self.make_response(None)
        self.make_response({"data": {"searchNotes": []}})

        status = create_note(self.args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assert_graphql(queries.search_notes, machine="lighthouse", key="python")
        self.assertEqual(print_mock.stderr.getvalue(), "No matches found\n")


def fake_editor(text=NOTE, returncode=0):
    def edit(args, check=False):
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, args)

        with open(args[1], "w", encoding="utf-8") as note_file:
            note_file.write(text)

        return mock.Mock(args=args, returncode=returncode)

    return edit


EXPECTED_SEARCH_OUTPUT = """\
Build: lighthouse/3363
Submitted: Sun Oct 24 01:18:45 2021 -0700
Completed: Sun Oct 24 01:24:08 2021 -0700
Published: no
Keep: no
Tags: 
Packages-built: None

foo



Build: lighthouse/3360
Submitted: Sat Oct 23 19:29:38 2021 -0700
Completed: Sat Oct 23 19:34:25 2021 -0700
Published: no
Keep: yes
Tags: 
Packages-built: None

foobar


"""
