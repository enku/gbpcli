"""Tests for the notes subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import os
import subprocess
from argparse import Namespace
from unittest import mock

from unittest_fixtures import depends, requires

from gbpcli.subcommands.notes import handler as create_note

from . import LOCAL_TIMEZONE, TestCase, make_response

MODULE = "gbpcli.subcommands.notes"
NOTE = "Hello world\n"


@depends("gbp")
def responses(_, fixtures) -> None:
    gbp = fixtures.gbp
    make_response(gbp, "status.json")
    make_response(gbp, "create_note.json")


def args(_options, _fixtures) -> Namespace:
    return Namespace(machine="lighthouse", number="3109", delete=False, search=False)


@requires("gbp", "console", responses, args)
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class NotesTestCase(TestCase):
    """notes tests"""

    maxDiff = None

    def assert_create_note(self, machine="lighthouse", number="3109", note=NOTE):
        """Assert that the note was created by a GraphQL request"""
        gbp = self.fixtures.gbp

        self.assert_graphql(
            gbp, gbp.query.gbpcli.build, index=0, id=f"{machine}.{number}"
        )
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.create_note,
            id=f"{machine}.{number}",
            index=1,
            note=note,
        )

    def test_create_with_editor(self):
        editor = fake_editor()
        gbp = self.fixtures.gbp
        console = self.fixtures.console

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, {"EDITOR": "foo"}, clear=True):
                    status = create_note(self.fixtures.args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_create_note()
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_create_with_editor_but_editor_fails_does_not_create_note(self):
        editor = fake_editor(returncode=1)
        gbp = self.fixtures.gbp
        console = self.fixtures.console

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, {"VISUAL": "foo"}, clear=True):
                    status = create_note(self.fixtures.args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(gbp.query._session.post.call_count, 1)
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_when_isatty_but_no_editor_reads_from_stdin(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                    status = create_note(self.fixtures.args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_create_note()

    def test_delete_deletes_note(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        self.fixtures.args.delete = True
        create_note(self.fixtures.args, gbp, console)

        self.assert_create_note(note=None)

    def test_create_with_no_tty(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "status.json")
        make_response(gbp, "create_note.json")

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=False):
            with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                create_note(self.fixtures.args, gbp, console)

        self.assert_create_note()

    def test_should_print_error_when_build_does_not_exist(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, None)
        make_response(gbp, {"data": {"build": None}})

        status = create_note(self.fixtures.args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.getvalue(), "Build not found\n")

    def test_should_print_error_when_invalid_number_given(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        self.fixtures.args.number = "foo"

        with self.assertRaises(SystemExit) as context:
            create_note(self.fixtures.args, gbp, console)

        self.assertEqual(context.exception.args, ("Invalid build ID: foo",))

    def test_search_notes(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        self.fixtures.args.search = True
        self.fixtures.args.number = "10,000"
        make_response(gbp, None)
        make_response(gbp, "search_notes.json")

        status = create_note(self.fixtures.args, gbp, console)

        # pylint: disable=duplicate-code
        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.search,
            machine="lighthouse",
            field="NOTES",
            key="10,000",
        )
        self.assertEqual(console.out.getvalue(), EXPECTED_SEARCH_OUTPUT)

    def test_search_no_matches_found(self):
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        self.fixtures.args.search = True
        self.fixtures.args.number = "python"
        make_response(gbp, None)
        make_response(gbp, {"data": {"search": []}})

        status = create_note(self.fixtures.args, gbp, console)

        self.assertEqual(status, 1)
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.search,
            machine="lighthouse",
            field="NOTES",
            key="python",
        )
        self.assertEqual(console.err.getvalue(), "No matches found\n")


def fake_editor(text=NOTE, returncode=0):
    def edit(args_, check=False):
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, args_)

        with open(args_[1], "w", encoding="utf-8") as note_file:
            note_file.write(text)

        return mock.Mock(args=args_, returncode=returncode)

    return edit


EXPECTED_SEARCH_OUTPUT = """\
Build: lighthouse/10000
Submitted: Thu Sep  1 09:28:12 2022 -0700
Completed: Thu Sep  1 09:47:34 2022 -0700
Published: no
Keep: yes
Tags: 10000
Packages-built: None

This is a note!

"""
