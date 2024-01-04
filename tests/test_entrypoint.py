"""Tests for the main module"""
# pylint: disable=missing-function-docstring,protected-access
import argparse
import importlib
import sys
import unittest
from unittest import mock

import gbpcli
import gbpcli.subcommands.list as list_subcommand
from gbpcli import build_parser, main
from gbpcli.graphql import APIError
from gbpcli.theme import get_theme_from_string

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
                    description=module.HELP,
                    formatter_class=argparse.RawTextHelpFormatter,
                )
                subparser = subparsers.add_parser.return_value
                subparser.set_defaults.assert_any_call(func=module.handler)


class GetArgumentsTestCase(unittest.TestCase):
    """Tests for the get_arguments function"""

    def test(self):
        argv = [
            "--url",
            "https://gbp.invalid/",
            "--my-machines",
            "lighthouse polaris",
            "list",
            "lighthouse",
        ]

        result = gbpcli.get_arguments(argv)

        expected = argparse.Namespace(
            url="https://gbp.invalid/",
            color="auto",
            my_machines="lighthouse polaris",
            machine="lighthouse",
            func=list_subcommand.handler,
        )
        self.assertEqual(result, expected)


class GetConsoleTestCase(unittest.TestCase):
    """Tests for the get_console function"""

    theme = get_theme_from_string("")

    def test_force_terminal_true(self):
        console = gbpcli.get_console(True, self.theme)

        self.assertEqual(console.out.is_terminal, True)

    def test_force_terminal_false(self):
        console = gbpcli.get_console(False, self.theme)

        self.assertEqual(console.out.is_terminal, False)

    def test_with_theme(self):
        theme = get_theme_from_string("rose=red:violet=blue")
        console = gbpcli.get_console(True, theme)
        output = [*console.out.render("[rose]rose[/rose][violet]violet[/violet]")]

        rose = output[0]
        self.assertEqual(rose.text, "rose")
        self.assertEqual(rose.style.color.name, "red")

        violet = output[1]
        self.assertEqual(violet.text, "violet")
        self.assertEqual(violet.style.color.name, "blue")


class MainTestCase(unittest.TestCase):
    """tests for the main function"""

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.argparse.ArgumentParser.parse_args")
    @mock.patch("gbpcli.Console")
    def test(self, console_mock, parse_args_mock, gbp_mock):
        parse_args_mock.return_value.url = "http://test.invalid/"
        parse_args_mock.return_value.color = "auto"
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
            with self.assertRaises(SystemExit) as context:
                main([])

        self.assertEqual(context.exception.args, (1,))
        print_help_mock.assert_called_once_with(file=sys.stderr)

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.rich.console.Console")
    def test_should_print_to_stderr_and_exit_1_on_exception(
        self, console_mock, gbp_mock
    ):
        error = APIError("blah", {})
        message = "blah"

        gbp_mock.return_value.get_build_info.side_effect = error
        status = main(["status", "lighthouse"])
        self.assertEqual(status, 1)
        console_mock.return_value.print.assert_called_once_with(message)
