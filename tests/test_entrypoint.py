"""Tests for the main module"""
# pylint: disable=missing-function-docstring
import argparse
import importlib
import sys
import unittest
from unittest import mock

from gbpcli import APIError, UnexpectedResponseError, build_parser, main

SUBCOMMANDS = [
    "diff",
    "latest",
    "list",
    "logs",
    "machines",
    "publish",
    "show",
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
                subparsers.add_parser.assert_any_call(subcommand, help=module.__doc__)
                subparser = subparsers.add_parser.return_value
                subparser.set_defaults.assert_any_call(func=module.handler)


class MainTestCase(unittest.TestCase):
    """tests for the main function"""

    @mock.patch("gbpcli.argparse.ArgumentParser.parse_args")
    def test(self, parse_args_mock):
        func = parse_args_mock.return_value.func
        func.return_value = 0
        argv = ["show", "lighthouse"]
        status = main(argv)

        func.assert_called_once_with(parse_args_mock.return_value)
        self.assertEqual(status, 0)

    def test_should_print_help_when_no_func(self):
        with mock.patch("gbpcli.argparse.ArgumentParser.print_help") as print_help_mock:
            status = main([])

        self.assertEqual(status, 1)
        print_help_mock.assert_called_once_with(file=sys.stderr)

    @mock.patch("gbpcli.argparse.ArgumentParser")
    @mock.patch("gbpcli.print")
    def test_should_print_to_stderr_and_exit_1_on_exception(
        self, print_mock, argument_parser_mock
    ):
        parser = argument_parser_mock.return_value
        args = parser.parse_args.return_value
        errors = [APIError("blah", {}), UnexpectedResponseError(mock.Mock())]
        messages = ["blah", "Unexpected server response"]

        for error, message in zip(errors, messages):
            with self.subTest(error=error, message=message):
                args.func.side_effect = error
                status = main([])
                self.assertEqual(status, 1)
                print_mock.assert_called_once_with(message, file=sys.stderr)
            print_mock.reset_mock()
