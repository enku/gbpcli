"""Tests for the diff subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from json import loads as parse
from unittest import mock

from gbp_testkit.helpers import parse_args, print_command
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.diff import handler as diff

from . import LOCAL_TIMEZONE, TestCase, http_response, load_data, make_response


@given("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class DiffTestCase(TestCase):
    """diff() tests"""

    def test_should_display_diffs(self, fixtures: Fixtures):
        cmdline = "gbp diff lighthouse 3111 3112"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "diff.json")

        print_command(cmdline, console)
        status = diff(args, gbp, console)

        self.assertEqual(status, 0)
        expected = """$ gbp diff lighthouse 3111 3112
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sun Oct  2 12:10:02 2022 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
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
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.diff, left="lighthouse.3111", right="lighthouse.3112"
        )

    def test_should_print_nothing_when_no_diffs(self, fixtures: Fixtures):
        cmdline = "gbp diff lighthouse 3111 3111"
        args = parse_args(cmdline)
        no_diffs_json = parse(load_data("diff_no_content.json"))
        gbp = fixtures.gbp
        console = fixtures.console
        gbp.query._session.post.return_value = http_response(json=no_diffs_json)

        diff(args, gbp, console)

        self.assertEqual(console.out.file.getvalue(), "")

    def test_when_right_is_none_should_use_latest(self, fixtures: Fixtures):
        cmdline = "gbp diff lighthouse 3111"
        args = parse_args(cmdline)
        latest_json = parse(load_data("list.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = fixtures.gbp
        console = fixtures.console
        gbp.query._session.post.side_effect = (
            http_response(json=latest_json),
            http_response(json=mock_diff_json),
        )

        status = diff(args, gbp, console)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call(
                gbp.query._url,
                json={
                    "query": gbp.query.gbpcli.builds.query,
                    "variables": {"machine": "lighthouse", "withPackages": False},
                },
            ),
            mock.call(
                gbp.query._url,
                json={
                    "query": gbp.query.gbpcli.diff.query,
                    "variables": {
                        "left": "lighthouse.3111",
                        "right": "lighthouse.10694",
                    },
                },
            ),
        ]
        gbp.query._session.post.assert_has_calls(expected_calls)

    def test_when_left_is_none_should_use_published(self, fixtures: Fixtures):
        cmdline = "gbp diff lighthouse"
        args = parse_args(cmdline)
        list_json = parse(load_data("list.json"))
        mock_diff_json = parse(load_data("diff.json"))
        gbp = fixtures.gbp
        console = fixtures.console
        gbp.query._session.post.side_effect = (
            http_response(json=list_json),
            http_response(json=mock_diff_json),
        )

        status = diff(args, gbp, console)

        self.assertEqual(status, 0)
        expected_calls = [
            mock.call(
                gbp.query._url,
                json={
                    "query": gbp.query.gbpcli.builds.query,
                    "variables": {"machine": "lighthouse", "withPackages": False},
                },
            ),
            mock.call(
                gbp.query._url,
                json={
                    "query": gbp.query.gbpcli.diff.query,
                    "variables": {
                        "left": "lighthouse.10678",
                        "right": "lighthouse.10694",
                    },
                },
            ),
        ]
        gbp.query._session.post.assert_has_calls(expected_calls)

    def test_when_left_is_none_and_not_published(self, fixtures: Fixtures):
        cmdline = "gbp diff jenkins"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        list_json = parse(load_data("list.json"))

        # Make sure there are not published builds
        for item in list_json["data"]["builds"]:
            item["published"] = False

        make_response(gbp, list_json)

        status = diff(args, gbp, console)

        self.assertEqual(status, 1)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.builds, machine="jenkins", withPackages=False
        )
        self.assertEqual(
            console.err.file.getvalue(), "No builds given and no builds published\n"
        )

    def test_against_missing_timestamps(self, fixtures: Fixtures):
        # Legacy builds have no (None) built field
        cmdline = "gbp diff lighthouse 3111 3112"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        mock_json = parse(load_data("diff.json"))

        # Emulate an old build where we didn't have a built field
        mock_json["data"]["diff"]["left"]["built"] = None

        make_response(gbp, mock_json)

        print_command(cmdline, console)
        status = diff(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(
            console.out.file.getvalue(),
            """$ gbp diff lighthouse 3111 3112
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sat Mar 20 11:57:21 2021 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
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
""",
        )
