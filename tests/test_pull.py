"""Tests for the pull subcommand"""
# pylint: disable=missing-function-docstring,no-self-use
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.pull import handler as pull

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PullTestCase(unittest.TestCase):
    """pull() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number=3226)
        mock_json = parse(load_data("pull.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        pull(args, gbp)

        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.pull,
                "variables": {"name": "lighthouse", "number": 3226},
            },
            headers=gbp.headers,
        )
