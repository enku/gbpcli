"""Tests for the main module"""

# pylint: disable=missing-function-docstring,protected-access,unused-argument
import argparse
import importlib
import os.path
import sys
import unittest
from unittest import mock

from unittest_fixtures import Fixtures, given

import gbpcli
import gbpcli.subcommands.list as list_subcommand
from gbpcli import build_parser, config, main
from gbpcli.graphql import APIError, auth_encode
from gbpcli.theme import get_theme_from_string

from . import TestCase

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


class GBPTests(unittest.TestCase):
    """Tests for the GBP class"""

    def test_auth(self):
        url = "http//test.invalid/"
        auth = {"user": "test", "api_key": "57cd9181-3de4-4696-adbb-6a3cfceec43e"}

        gbp = gbpcli.GBP(url, auth=auth)

        expected = (
            f'Basic {auth_encode("test", "57cd9181-3de4-4696-adbb-6a3cfceec43e")}'
        )
        self.assertEqual(gbp.query._session.headers["Authorization"], expected)


class BuildParserTestCase(unittest.TestCase):
    """build_parser() tests"""

    @mock.patch("gbpcli.argparse.ArgumentParser.add_subparsers")
    def test(self, add_subparsers_mock):
        parser = build_parser(config.Config())

        self.assertIsInstance(parser, argparse.ArgumentParser)
        subparsers = add_subparsers_mock.return_value
        self.assertGreaterEqual(subparsers.add_parser.call_count, len(SUBCOMMANDS))

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

        result = gbpcli.get_arguments(config.Config(), argv)

        expected = argparse.Namespace(
            url="https://gbp.invalid/",
            color="auto",
            my_machines="lighthouse polaris",
            machine="lighthouse",
            func=list_subcommand.handler,
        )
        self.assertEqual(result, expected)

    def test_with_config(self):
        argv = ["list", "lighthouse"]
        user_config = config.Config(
            url="https://gbp.invalid/", my_machines=["lighthouse", "polaris"]
        )

        result = gbpcli.get_arguments(user_config, argv)

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


@given("gbp", "tmpdir", "user_config_dir", "console")
class MainTestCase(TestCase):
    """tests for the main function"""

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.argparse.ArgumentParser.parse_args")
    @mock.patch("gbpcli.Console")
    def test(self, console_mock, parse_args_mock, gbp_mock, fixtures: Fixtures):
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

    def test_should_print_help_when_no_func(self, fixtures: Fixtures):
        with mock.patch("gbpcli.argparse.ArgumentParser.print_help") as print_help_mock:
            with self.assertRaises(SystemExit) as context:
                main([])

        self.assertEqual(context.exception.args, (1,))
        print_help_mock.assert_called_once_with(file=sys.stderr)

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.rich.console.Console")
    def test_should_print_to_stderr_and_exit_1_on_exception(
        self, console_mock, gbp_mock, fixtures: Fixtures
    ):
        error = APIError("blah", {})
        message = "blah"

        gbp_mock.return_value.get_build_info.side_effect = error
        status = main(["status", "lighthouse"])
        self.assertEqual(status, 1)
        console_mock.return_value.print.assert_called_once_with(message)

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.argparse.ArgumentParser.parse_args")
    @mock.patch("gbpcli.Console")
    def test_should_instantiate_gbp_with_api_key_when_available(
        self, _mock_console, mock_parse_args, mock_gbp, fixtures: Fixtures
    ):
        mock_gbp.return_value = fixtures.gbp
        mock_parse_args.return_value.url = "http://test.invalid/"
        mock_parse_args.return_value.color = "auto"
        func = mock_parse_args.return_value.func
        func.return_value = 0

        filename = os.path.join(fixtures.tmpdir, "gbpcli.toml")
        with open(filename, "wb") as fp:
            os.chmod(fp.fileno(), 0o600)
            fp.write(b"[gbpcli]\n")
            fp.write(b'auth = { user = "test", api_key = "secret" }\n')

        main(["status", "lighthouse"])

        mock_gbp.assert_called_once_with(
            "http://test.invalid/", auth={"user": "test", "api_key": "secret"}
        )

    @mock.patch("gbpcli.GBP")
    @mock.patch("gbpcli.Console")
    def test_with_config_file_option(
        self, _mock_console, mock_gbp, fixtures: Fixtures
    ) -> None:
        mock_gbp.return_value = fixtures.gbp
        tmpdir = fixtures.tmpdir

        filename = os.path.join(tmpdir, "custom.toml")
        with open(filename, "wb") as fp:
            fp.write(b'[gbpcli]\nurl = "http://fromconfig.invalid/"\n')

        with mock.patch.dict(os.environ, {"GBPCLI_CONFIG": filename}):
            main(["status", "lighthouse"])

        mock_gbp.assert_called_once_with("http://fromconfig.invalid/", auth=None)

    def test_main_no_args(self, fixtures: Fixtures) -> None:
        # admittedly this is mostly to get a good screenshot
        console = fixtures.console

        console.out.print("[green]$ [/green]gbp")

        def mock_write(data: str):
            console.out.print(data, end="")

        with mock.patch("gbpcli.sys.stderr.write", mock_write):
            with self.assertRaises(SystemExit) as exc_info:
                main([])

        exception = exc_info.exception
        self.assertEqual(exception.args, (1,))


@given("gbp", "tmpdir", "user_config_dir")
class GetUserConfigTests(TestCase):
    """Tests for the get_user_config function"""

    def test_with_config(self, fixtures: Fixtures) -> None:
        filename = os.path.join(fixtures.tmpdir, "gbpcli.toml")

        with open(filename, "wb") as fp:
            fp.write(
                b"""\
[gbpcli]
url = "http://test.invalid/"
my_machines = ["this", "that", "the_other"]
"""
            )

        user_config = gbpcli.get_user_config()

        self.assertEqual(user_config.url, "http://test.invalid/")
        self.assertEqual(user_config.my_machines, ["this", "that", "the_other"])

    def test_with_no_config(self, fixtures: Fixtures) -> None:
        user_config = gbpcli.get_user_config()

        self.assertEqual(user_config.url, None)
        self.assertEqual(user_config.my_machines, None)

    def test_with_given_config(self, fixtures: Fixtures) -> None:
        custom_filename = os.path.join(fixtures.tmpdir, "custom.toml")

        with open(custom_filename, "wb") as fp:
            fp.write(
                b"""\
[gbpcli]
url = "http://test.invalid/"
my_machines = ["this", "that", "the_other"]
"""
            )

        user_config = gbpcli.get_user_config(custom_filename)

        self.assertEqual(user_config.url, "http://test.invalid/")
        self.assertEqual(user_config.my_machines, ["this", "that", "the_other"])

    def test_with_given_config_that_does_not_exist(self, fixtures: Fixtures) -> None:
        custom_filename = os.path.join(fixtures.tmpdir, "bogus.toml")

        with self.assertRaises(FileNotFoundError):
            gbpcli.get_user_config(custom_filename)


class EnsureArgsHasFuncTests(TestCase):
    """Tests for the ensure_args_has_func helper function"""

    def test_has_func(self) -> None:
        args = argparse.Namespace(func=lambda: None)
        parser = mock.Mock()

        gbpcli.ensure_args_has_func(args, parser)

    def test_has_no_func(self) -> None:
        args = argparse.Namespace()
        parser = mock.Mock()

        with self.assertRaises(SystemExit) as exc_info:
            gbpcli.ensure_args_has_func(args, parser)

        exception = exc_info.exception
        self.assertEqual(exception.args, (1,))
        parser.print_help.assert_called_once_with(file=sys.stderr)
