"""Tests for the diff subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.diff import handler as diff

from . import LOCAL_TIMEZONE, TestCase, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.utils.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.diff")
class DiffTestCase(TestCase):
    """diff() tests"""

    def test_should_display_diffs(self, _print_mock):
        args = Namespace(machine="lighthouse", left="3111", right="3112")
        self.make_response("diff.json")

        status = diff(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        expected = """\
diff -r lighthouse/3111 lighthouse/3112
--- a/lighthouse/3111 Sun Oct  2 12:10:02 2022 -0700
+++ b/lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
-app-accessibility/at-spi2-atk-2.38.0-1
+app-accessibility/at-spi2-atk-2.46.0-1
-app-accessibility/at-spi2-core-2.44.1-1
+app-accessibility/at-spi2-core-2.46.0-1
-dev-libs/atk-2.38.0-3
+dev-libs/atk-2.46.0-1
-dev-libs/libgusb-0.4.0-1
+dev-libs/libgusb-0.4.1-1
-sys-kernel/vanilla-sources-5.19.12-1
+sys-kernel/vanilla-sources-6.0.0-1
"""
        self.assertEqual(self.console.getvalue(), expected)
        self.assert_graphql(
            queries.diff, left="lighthouse.3111", right="lighthouse.3112"
        )

    def test_should_print_nothing_when_no_diffs(self, _print_mock):
        args = Namespace(machine="lighthouse", left="3111", right="3111")
        no_diffs_json = parse(load_data("diff_no_content.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=no_diffs_json)

        diff(args, gbp, self.console)

        self.assertEqual(self.console.getvalue(), "")

    def test_when_right_is_none_should_use_latest(self, _print_mock):
        args = Namespace(machine="lighthouse", left="3111", right=None)
        latest_json = parse(load_data("latest.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = make_gbp()
        gbp.session.post.side_effect = (
            make_response(json=latest_json),
            make_response(json=mock_diff_json),
        )

        status = diff(args, gbp, self.console)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call(
                gbp.url,
                json={"query": queries.latest, "variables": {"machine": "lighthouse"}},
                headers=gbp.headers,
            ),
            mock.call(
                gbp.url,
                json={
                    "query": queries.diff,
                    "variables": {
                        "left": "lighthouse.3111",
                        "right": "lighthouse.3113",
                    },
                },
                headers=gbp.headers,
            ),
        ]
        gbp.session.post.assert_has_calls(expected_calls)

    def test_when_left_is_none_should_use_published(self, _print_mock):
        args = Namespace(machine="lighthouse", left=None, right=None)
        list_json = parse(load_data("list.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = make_gbp()
        gbp.session.post.side_effect = (
            make_response(json=list_json),
            make_response(json=mock_diff_json),
        )

        status = diff(args, gbp, self.console)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call(
                gbp.url,
                json={"query": queries.builds, "variables": {"machine": "lighthouse"}},
                headers=gbp.headers,
            ),
            mock.call(
                gbp.url,
                json={
                    "query": queries.diff,
                    "variables": {
                        "left": "lighthouse.10678",
                        "right": "lighthouse.10694",
                    },
                },
                headers=gbp.headers,
            ),
        ]
        gbp.session.post.assert_has_calls(expected_calls)

    def test_when_left_is_none_and_not_published(self, print_mock):
        args = Namespace(machine="jenkins", left=None, right=None)
        list_json = parse(load_data("list.json"))

        # Make sure there are not published builds
        for item in list_json["data"]["builds"]:
            item["published"] = False

        self.make_response(list_json)

        status = diff(args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assert_graphql(queries.builds, machine="jenkins")
        self.assertEqual(
            print_mock.stderr.getvalue(),
            "No origin specified and no builds published\n",
        )
