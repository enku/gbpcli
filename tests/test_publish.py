"""Tests for the publish subcommand"""
# pylint: disable=missing-function-docstring,no-self-use
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.publish import handler as publish

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PublishTestCase(TestCase):
    """publish() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number=3109)
        self.make_response("publish.json")

        publish(args, self.gbp)

        self.assert_graphql(queries.publish, name="lighthouse", number=3109)

    def test_should_get_latest_when_number_is_none(self):
        args = Namespace(machine="lighthouse", number=None)
        self.make_response({"data": {"latest": {"number": 2080}}})
        self.make_response("publish.json")

        status = publish(args, self.gbp)

        self.assertEqual(status, 0)
        self.assert_graphql(queries.latest, index=0, name="lighthouse")
        self.assert_graphql(queries.publish, index=1, name="lighthouse", number=2080)
