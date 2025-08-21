"""Tests for the notes subcommand"""

# pylint: disable=missing-function-docstring
import datetime as dt
import os
import subprocess
from unittest import mock

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args, print_command
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, fixture, given

from gbpcli.subcommands.notes import handler as create_note

from . import lib

MODULE = "gbpcli.subcommands.notes"
NOTE = "Hello world\n"

args = parse_args("gbp notes lighthouse 3109")
build = Build(machine="lighthouse", build_id="3109")


@fixture(testkit.publisher)
def pulled_build(_: Fixtures) -> None:
    timestamp = dt.datetime(2025, 8, 21, 16, 8)
    publisher.pull(build)
    record = publisher.record(build)
    publisher.save(record, submitted=timestamp, completed=timestamp)


@given(pulled_build, testkit.gbp, testkit.console, lib.local_timezone)
class NotesTestCase(lib.TestCase):
    """notes tests"""

    def assert_create_note(
        self, fixtures: Fixtures, machine="lighthouse", number="3109", note=NOTE
    ):
        """Assert that the note was created by a GraphQL request"""
        gbp = fixtures.gbp

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

    def test_create_with_editor(self, fixtures: Fixtures):
        editor = fake_editor()
        gbp = fixtures.gbp
        console = fixtures.console

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, VISUAL="foo"):
                    status = create_note(args, gbp, console)

        self.assertEqual(status, 0)
        record = publisher.record(build)
        self.assertEqual(record.note, NOTE)
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_create_with_editor_but_editor_fails_does_not_create_note(
        self, fixtures: Fixtures
    ):
        editor = fake_editor(returncode=1)
        gbp = fixtures.gbp
        console = fixtures.console

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
                with mock.patch.dict(os.environ, VISUAL="foo"):
                    status = create_note(args, gbp, console)

        self.assertEqual(status, 1)
        record = publisher.record(build)
        self.assertEqual(record.note, None)
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_when_isatty_but_no_editor_reads_from_stdin(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=True):
            with mock.patch.dict(os.environ):
                os.environ.pop("VISUAL", None)
                os.environ.pop("EDITOR", None)
                with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                    status = create_note(args, gbp, console)

        self.assertEqual(status, 0)
        record = publisher.record(build)
        self.assertEqual(record.note, NOTE)

    def test_delete_deletes_note(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        d_args = parse_args("gbp notes -d lighthouse 3109")
        record = publisher.record(build)
        publisher.repo.build_records.save(record, note=NOTE)

        status = create_note(d_args, gbp, console)

        self.assertEqual(status, 0)
        record = publisher.record(build)
        self.assertEqual(record.note, None)

    def test_create_with_no_tty(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console

        with mock.patch(f"{MODULE}.sys.stdin.isatty", return_value=False):
            with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
                create_note(args, gbp, console)

        record = publisher.record(build)
        self.assertEqual(record.note, NOTE)

    def test_should_print_error_when_build_does_not_exist(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        s_args = parse_args("gbp notes lighthouse 9999")

        status = create_note(s_args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Build not found\n")

    def test_should_print_error_when_invalid_number_given(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        my_args = parse_args("gbp notes lighthouse foo")

        with self.assertRaises(SystemExit) as context:
            create_note(my_args, gbp, console)

        self.assertEqual(context.exception.args, ("Invalid build ID: foo",))

    def test_search_notes(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        record = publisher.record(build)
        publisher.save(record, note="10,000 maniacs")
        s_args = parse_args("gbp notes -s lighthouse 10,000")

        print_command("gbp notes --search lighthouse note", console)
        with mock.patch.object(
            gbp.query.gbpcli, "search", wraps=gbp.query.gbpcli.search
        ) as search:
            status = create_note(s_args, gbp, console)

        # pylint: disable=duplicate-code
        self.assertEqual(status, 0)
        search.assert_called_once_with(
            machine="lighthouse", field="NOTES", key="10,000"
        )
        self.assertEqual(console.out.file.getvalue(), EXPECTED_SEARCH_OUTPUT)

    def test_search_no_matches_found(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        console = fixtures.console
        s_args = parse_args("gbp notes -s lighthouse python")

        with mock.patch.object(
            gbp.query.gbpcli, "search", wraps=gbp.query.gbpcli.search
        ) as search:
            status = create_note(s_args, gbp, console)

        self.assertEqual(status, 1)
        search.assert_called_once_with(
            machine="lighthouse", field="NOTES", key="python"
        )
        self.assertEqual(console.err.file.getvalue(), "No matches found\n")


def fake_editor(text=NOTE, returncode=0):
    def edit(args_, check=False):
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, args_)

        with open(args_[1], "w", encoding="utf-8") as note_file:
            note_file.write(text)

        return mock.Mock(args=args_, returncode=returncode)

    return edit


EXPECTED_SEARCH_OUTPUT = """$ gbp notes --search lighthouse note
Build: lighthouse/3109
Submitted: Thu Aug 21 14:08:00 2025 -0700
Completed: Thu Aug 21 14:08:00 2025 -0700
Published: no
Keep: no
Tags: 
Packages-built: None

10,000 maniacs

"""
