"""Tests for the publish subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from gbp_testkit.helpers import parse_args
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.publish import handler as publish

from . import LOCAL_TIMEZONE, TestCase, make_response


@given("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PublishTestCase(TestCase):
    """publish() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp publish lighthouse 3109"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "publish.json")

        publish(args, gbp, console)

        self.assert_graphql(gbp, gbp.query.gbpcli.publish, id="lighthouse.3109")

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        cmdline = "gbp publish lighthouse"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"latest": {"id": "lighthouse.2080"}}})
        make_response(gbp, "publish.json")

        status = publish(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(gbp, gbp.query.gbpcli.latest, index=0, machine="lighthouse")
        self.assert_graphql(
            gbp, gbp.query.gbpcli.publish, index=1, id="lighthouse.2080"
        )
