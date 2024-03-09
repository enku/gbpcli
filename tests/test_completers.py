"""Tests for the completers module"""

# pylint: disable=missing-docstring

from argparse import Namespace
from unittest import mock

from gbpcli import GBP
from gbpcli.subcommands import completers
from gbpcli.types import Build

from . import TestCase


def patch_gbp(func):
    return mock.patch("gbpcli.subcommands.completers.GBP", spec=GBP)(func)


@patch_gbp
class MachinesTests(TestCase):
    def test(self, mock_gbp) -> None:
        gbp = mock_gbp.return_value
        gbp.machines.return_value = [("lighthouse",), ("babette",)]
        parsed_args = Namespace(url="http://gbp.invalid/")

        self.assertEqual(
            completers.machines(
                prefix="", action=None, parser=None, parsed_args=parsed_args
            ),
            ["lighthouse", "babette"],
        )

    def test_with_prefix(self, mock_gbp):
        gbp = mock_gbp.return_value
        gbp.machines.return_value = [("lighthouse",), ("babette",)]
        parsed_args = Namespace(url="http://gbp.invalid/")

        self.assertEqual(
            completers.machines(
                prefix="l", action=None, parser=None, parsed_args=parsed_args
            ),
            ["lighthouse"],
        )


@patch_gbp
class BuildIDsTests(TestCase):
    def test(self, mock_gbp) -> None:
        gbp = mock_gbp.return_value
        gbp.builds.return_value = [
            make_build("lighthouse", 1),
            make_build("lighthouse", 2),
            make_build("lighthouse", 12),
        ]

        parsed_args = Namespace(url="http://gbp.invalid/", machine="lighthouse")
        build_ids = completers.build_ids(
            prefix="", action=None, parser=None, parsed_args=parsed_args
        )

        self.assertEqual(build_ids, ["1", "2", "12"])

    def test_with_prefix(self, mock_gbp) -> None:
        gbp = mock_gbp.return_value
        gbp.builds.return_value = [
            make_build("lighthouse", 1),
            make_build("lighthouse", 2),
            make_build("lighthouse", 12),
        ]

        parsed_args = Namespace(url="http://gbp.invalid/", machine="lighthouse")
        build_ids = completers.build_ids(
            prefix="1", action=None, parser=None, parsed_args=parsed_args
        )

        self.assertEqual(build_ids, ["1", "12"])


def make_build(machine: str, number: int) -> Build:
    return Build(machine=machine, number=number)
