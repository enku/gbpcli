"""Tests for the diff subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.diff import handler as diff

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.diff")
class DiffTestCase(unittest.TestCase):
    """diff() tests"""

    def test_should_display_diffs(self, print_mock):
        args = Namespace(machine="lighthouse", left=2083, right=2084)
        mock_json = parse(load_data("diff.json"))
        gbp = make_gbp()
        gbp.session.get.return_value = make_response(json=mock_json)

        status = diff(args, gbp)

        self.assertEqual(status, 0)
        expected = """\
diff -r lighthouse/2083 lighthouse/2084
--- a/lighthouse/2083 Tue Jul 20 17:22:03 2021 -0700
+++ b/lighthouse/2084 Tue Jul 20 18:27:18 2021 -0700
-sys-libs/pam-1.5.1_p20210610-1
+sys-libs/pam-1.5.1-1
"""
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        gbp.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/diff/2083/2084"
        )

    def test_should_print_nothing_when_no_diffs(self, print_mock):
        args = Namespace(machine="lighthouse", left=2083, right=2084)
        no_diffs_json = parse(load_data("diff_no_content.json"))
        gbp = make_gbp()
        gbp.session.get.return_value = make_response(json=no_diffs_json)

        diff(args, gbp)

        self.assertEqual(print_mock.stdout.getvalue(), "")

    def test_when_right_is_none_should_use_latest(self, _print_mock):
        args = Namespace(machine="lighthouse", left=2083, right=None)
        latest_json = parse(load_data("latest.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = make_gbp()
        gbp.session.get.side_effect = (
            make_response(json=latest_json),
            make_response(json=mock_diff_json),
        )

        status = diff(args, gbp)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call("http://test.invalid/api/builds/lighthouse/latest"),
            mock.call("http://test.invalid/api/builds/lighthouse/diff/2083/2085"),
        ]
        gbp.session.get.assert_has_calls(expected_calls)

    def test_when_left_is_none_should_use_published(self, _print_mock):
        args = Namespace(machine="lighthouse", left=None, right=None)
        list_json = parse(load_data("list.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = make_gbp()
        gbp.session.get.side_effect = (
            make_response(json=list_json),
            make_response(json=mock_diff_json),
        )

        status = diff(args, gbp)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call("http://test.invalid/api/builds/lighthouse/"),
            mock.call("http://test.invalid/api/builds/lighthouse/diff/2080/2086"),
        ]
        gbp.session.get.assert_has_calls(expected_calls)

    def test_when_left_is_none_and_not_published(self, print_mock):
        args = Namespace(machine="lighthouse", left=None, right=None)
        list_json = parse(load_data("list.json"))

        # Make sure there are not published builds
        for item in list_json["builds"]:
            item["storage"]["published"] = False

        gbp = make_gbp()
        gbp.session.get.return_value = make_response(json=list_json)

        status = diff(args, gbp)

        self.assertEqual(status, 1)
        gbp.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/"
        )
        self.assertEqual(
            print_mock.stderr.getvalue(),
            "No origin specified and no builds published\n",
        )
