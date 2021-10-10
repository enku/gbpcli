"""Tests for the keep subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse

from gbpcli import queries
from gbpcli.subcommands.keep import handler as keep

from . import load_data, make_gbp, make_response, mock_print


class KeepTestCase(unittest.TestCase):
    """keep() tests"""

    maxDiff = None

    def test_keep(self):
        args = Namespace(machine="lighthouse", number=3210, release=False)
        mock_json = parse(load_data("keep_build.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = keep(args, gbp)

        self.assertEqual(status, 0)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.keep_build,
                "variables": {"name": "lighthouse", "number": 3210},
            },
            headers=gbp.headers,
        )

    @mock_print("gbpcli.subcommands.keep")
    def test_keep_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number=3210, release=False)
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"keepBuild": None}}
        )

        status = keep(args, gbp)
        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")

    def test_release(self):
        args = Namespace(machine="lighthouse", number=3210, release=True)
        mock_json = parse(load_data("release_build.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = keep(args, gbp)

        self.assertEqual(status, 0)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.release_build,
                "variables": {"name": "lighthouse", "number": 3210},
            },
            headers=gbp.headers,
        )

    @mock_print("gbpcli.subcommands.keep")
    def test_release_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number=3210, release=True)
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"releaseBuild": None}}
        )

        status = keep(args, gbp)
        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
