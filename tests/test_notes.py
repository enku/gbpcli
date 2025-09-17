"""Tests for the notes subcommand"""

# pylint: disable=missing-function-docstring
import os
import subprocess
from unittest import TestCase, mock

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given, where

from . import lib

BUILD = Build(machine="lighthouse", build_id="3109")
CMDLINE = "gbp notes lighthouse 3109"
MODULE = "gbpcli.subcommands.notes"
NOTE = "Hello world\n"


@given(testkit.environ)
@where(environ__clear=True)
@given(isatty=testkit.patch)
@where(isatty__target=f"{MODULE}.sys.stdin.isatty")
@where(isatty__return_value=True)
@given(lib.pulled_build, testkit.gbpcli, local_timezone=testkit.patch)
@where(pulled_build__build=BUILD)
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
class NotesTestCase(TestCase):
    """notes tests"""

    def test_create_with_editor(self, fixtures: Fixtures):
        editor = fake_editor()
        os.environ["VISUAL"] = "foo"

        with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
            status = fixtures.gbpcli(CMDLINE)

        self.assertEqual(status, 0)
        record = publisher.record(BUILD)
        self.assertEqual(record.note, NOTE)
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_create_with_editor_but_editor_fails_does_not_create_note(
        self, fixtures: Fixtures
    ):
        editor = fake_editor(returncode=1)
        os.environ["VISUAL"] = "foo"

        with mock.patch(f"{MODULE}.subprocess.run", wraps=editor) as run:
            status = fixtures.gbpcli(CMDLINE)

        self.assertEqual(status, 1)
        record = publisher.record(BUILD)
        self.assertEqual(record.note, None)
        run.assert_called_once_with(["foo", mock.ANY], check=False)

    def test_when_isatty_but_no_editor_reads_from_stdin(self, fixtures: Fixtures):
        os.environ.pop("EDITOR", None)
        os.environ.pop("EDITOR", None)

        with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
            status = fixtures.gbpcli(CMDLINE)

        self.assertEqual(status, 0)
        record = publisher.record(BUILD)
        self.assertEqual(record.note, NOTE)

    def test_delete_deletes_note(self, fixtures: Fixtures):
        record = publisher.record(BUILD)
        publisher.repo.build_records.save(record, note=NOTE)

        status = fixtures.gbpcli("gbp notes -d lighthouse 3109")

        self.assertEqual(status, 0)
        record = publisher.record(BUILD)
        self.assertEqual(record.note, None)

    def test_create_with_no_tty(self, fixtures: Fixtures):
        fixtures.isatty.return_value = False

        with mock.patch(f"{MODULE}.sys.stdin.read", return_value=NOTE):
            fixtures.gbpcli(CMDLINE)

        record = publisher.record(BUILD)
        self.assertEqual(record.note, NOTE)

    def test_should_print_error_when_build_does_not_exist(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp notes lighthouse 9999")

        self.assertEqual(status, 1)
        self.assertEqual(fixtures.console.stderr, "Build not found\n")

    def test_should_print_error_when_invalid_number_given(self, fixtures: Fixtures):
        with self.assertRaises(SystemExit) as context:
            fixtures.gbpcli("gbp notes lighthouse foo")

        self.assertEqual(context.exception.args, ("Invalid build ID: 'foo'",))

    def test_search_notes(self, fixtures: Fixtures):
        record = publisher.record(BUILD)
        publisher.save(record, note="10,000 maniacs")

        with mock.patch.object(
            fixtures.gbp.query.gbpcli, "search", wraps=fixtures.gbp.query.gbpcli.search
        ) as search:
            status = fixtures.gbpcli("gbp notes -s lighthouse 10,000")

        # pylint: disable=duplicate-code
        self.assertEqual(status, 0)
        search.assert_called_once_with(
            machine="lighthouse", field="NOTES", key="10,000"
        )
        self.assertEqual(fixtures.console.stdout, EXPECTED_SEARCH_OUTPUT)

    def test_search_no_matches_found(self, fixtures: Fixtures):
        with mock.patch.object(
            fixtures.gbp.query.gbpcli, "search", wraps=fixtures.gbp.query.gbpcli.search
        ) as search:
            status = fixtures.gbpcli("gbp notes -s lighthouse python")

        self.assertEqual(status, 1)
        search.assert_called_once_with(
            machine="lighthouse", field="NOTES", key="python"
        )
        self.assertEqual(fixtures.console.stderr, "No matches found\n")


def fake_editor(text=NOTE, returncode=0):
    def edit(args_, check=False):
        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, args_)

        with open(args_[1], "w", encoding="utf-8") as note_file:
            note_file.write(text)

        return mock.Mock(args=args_, returncode=returncode)

    return edit


EXPECTED_SEARCH_OUTPUT = """$ gbp notes -s lighthouse 10,000
Build: lighthouse/3109
Submitted: Fri Nov 12 21:25:53 2021 -0700
Completed: Fri Nov 12 21:29:34 2021 -0700
Published: no
Keep: no
Tags: 
Packages-built: None

10,000 maniacs

"""
