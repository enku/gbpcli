"""Tests for the diff subcommand"""
# pylint: disable=missing-function-docstring
import io
import unittest
from functools import partial
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.diff import handler as diff

from . import LOCAL_TIMEZONE, load_data, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.diff.print")
class DiffTestCase(unittest.TestCase):
    """diff() tests"""

    def test_should_display_diffs(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", left=2083, right=2084
        )
        mock_json = parse(load_data("diff.json"))
        args_mock.session.get.return_value = make_response(json=mock_json)

        diff(args_mock)

        expected = """\
diff -r lighthouse/2083 lighthouse/2084
--- a/lighthouse/2083 Tue Jul 20 17:22:03 2021 -0700
+++ b/lighthouse/2084 Tue Jul 20 18:27:18 2021 -0700
-sys-libs/pam-1.5.1_p20210610-1
+sys-libs/pam-1.5.1-1
"""
        self.assertEqual(stdout.getvalue(), expected)
        args_mock.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/diff/2083/2084"
        )

    def test_should_print_nothing_when_no_diffs(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", left=2083, right=2084
        )
        no_diffs_json = {"error": None, "diff": {"items": []}}
        args_mock.session.get.return_value = make_response(json=no_diffs_json)

        diff(args_mock)

        self.assertEqual(stdout.getvalue(), "")
