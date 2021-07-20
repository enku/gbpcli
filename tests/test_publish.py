"""Tests for the publish subcommand"""
# pylint: disable=missing-function-docstring,no-self-use
import unittest
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.publish import handler as publish

from . import LOCAL_TIMEZONE, load_data, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PublishTestCase(unittest.TestCase):
    """publish() tests"""

    def test(self):
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2086
        )
        mock_json = parse(load_data("publish.json"))
        args_mock.session.post.return_value = make_response(json=mock_json)

        publish(args_mock)

        args_mock.session.post.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2086/publish"
        )
