"""Tests for the main module"""
# pylint: disable=missing-function-docstring
import argparse
import importlib
import sys
import unittest
from unittest import mock

from gbpcli import APIError, build_parser, main

SUBCOMMANDS = [
    "build",
    "diff",
    "inspect",
    "keep",
    "latest",
    "list",
    "logs",
    "machines",
    "notes",
    "packages",
    "publish",
    "pull",
    "status",
    "tag",
]


class BuildParserTestCase(unittest.TestCase):
    """build_parser() tests"""

    @mock.patch("gbpcli.argparse.ArgumentParser.add_subparsers")
    def test(self, add_subparsers_mock):
        parser = build_parser()

        self.assertIsInstance(parser, argparse.ArgumentParser)
        subparsers = add_subparsers_mock.return_value
        self.assertEqual(subparsers.add_parser.call_count, len(SUBCOMMANDS))

        for subcommand in SUBCOMMANDS:
            with self.subTest(subcommand=subcommand):
                module = importlib.import_module(f"gbpcli.subcommands.{subcommand}")
                subparsers.add_parser.assert_any_call(
                    subcommand,
                    description=module.__doc__,
                    formatter_class=argparse.RawTextHelpFormatter,
                )
                subparser = subparsers.add_parser.return_value
                subparser.set_defaults.assert_any_call(func=module.handler)


class MainTestCase(unittest.TestCase):
    """tests for the main function"""

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.argparse.ArgumentParser.parse_args")
    @mock.patch("gbpcli.rich.console.Console")
    def test(self, console_mock, parse_args_mock, gbp_mock):
        parse_args_mock.return_value.url = "http://test.invalid/"
        func = parse_args_mock.return_value.func
        func.return_value = 0
        argv = ["status", "lighthouse"]
        status = main(argv)

        func.assert_called_once_with(
            parse_args_mock.return_value,
            gbp_mock.return_value,
            console_mock.return_value,
        )
        self.assertEqual(status, 0)

    def test_should_print_help_when_no_func(self):
        with mock.patch("gbpcli.argparse.ArgumentParser.print_help") as print_help_mock:
            status = main([])

        self.assertEqual(status, 1)
        print_help_mock.assert_called_once_with(file=sys.stderr)

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.print")
    def test_should_print_to_stderr_and_exit_1_on_exception(self, print_mock, gbp_mock):
        error = APIError("blah", {})
        message = "blah"

        gbp_mock.return_value.get_build_info.side_effect = error
        status = main(["status", "lighthouse"])
        self.assertEqual(status, 1)
        print_mock.assert_called_once_with(message, file=sys.stderr)
