"""Tests for the publish subcommand"""
# pylint: disable=missing-function-docstring,no-self-use
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.publish import handler as publish

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PublishTestCase(unittest.TestCase):
    """publish() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number=2086)
        mock_json = parse(load_data("publish.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        publish(args, gbp)

        gbp.session.post.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2086/publish"
        )

    def test_should_get_latest_when_number_is_none(self):
        args = Namespace(machine="lighthouse", number=None)
        mock_latest = make_response(json={"error": None, "number": 2080})
        mock_json = parse(load_data("publish.json"))
        gbp = make_gbp()
        gbp.session.get.return_value = mock_latest
        gbp.session.post.return_value = make_response(json=mock_json)

        status = publish(args, gbp)

        self.assertEqual(status, 0)
        gbp.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/latest"
        )
        gbp.session.post.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2080/publish"
        )
