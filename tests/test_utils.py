"""Tests for the "utils" module"""

# pylint: disable=missing-docstring,unused-argument
import argparse
import os
import sys
from unittest import TestCase, mock

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import types as gbp_types
from unittest_fixtures import Fixtures, given, where

from gbpcli.graphql import APIError, check
from gbpcli.types import Build
from gbpcli.utils import get_my_machines_from_args, load_env, re_path, resolve_build_id

from . import lib


class CheckTestCase(TestCase):
    """check() tests"""

    def test_should_raise_apierror_if_query_response_has_errors(self):
        error1 = {"message": "The end is near", "locations": [], "path": None}
        error2 = {"message": "Oh no!", "locations": [], "path": None}
        query_result = ({"build": None}, [error1, error2])

        with self.assertRaises(APIError) as context:
            check(query_result)

        exception = context.exception
        self.assertEqual(exception.args[0], [error1, error2])
        self.assertEqual(exception.data, {"build": None})


@given(testkit.gbp, lib.pulled_build)
@where(pulled_build__build=gbp_types.Build(machine="lighthouse", build_id="123"))
class ResolveBuildIdTestCase(TestCase):
    """resolve_build_id() tests"""

    def test_returns_latest_build_for_machine_when_build_id_is_none(
        self, fixtures: Fixtures
    ):
        result = resolve_build_id("lighthouse", None, gbp=fixtures.gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_build_id_is_none_and_no_latest(self, fixtures: Fixtures):
        with self.assertRaises(SystemExit) as context:
            resolve_build_id("bogus", None, gbp=fixtures.gbp)

        self.assertEqual(context.exception.args, ("No builds for bogus",))

    def test_returns_build_when_given_tag(self, fixtures: Fixtures):
        fixtures.publisher.tag(fixtures.pulled_build, "prod")

        result = resolve_build_id("lighthouse", "@prod", gbp=fixtures.gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_given_tag_that_does_not_exist(self, fixtures: Fixtures):
        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", "@prod", gbp=fixtures.gbp)

        self.assertEqual(
            context.exception.args, ("No such tag for lighthouse: 'prod'",)
        )

    def test_returns_build_with_given_id_if_given_build_id_is_numeric(
        self, fixtures: Fixtures
    ):
        gbp = fixtures.gbp

        result = resolve_build_id("lighthouse", "456", gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=456))

    def test_latest_build_tag(self, fixtures: Fixtures) -> None:
        """'@@' refers to the latest build for a machine"""
        result = resolve_build_id("lighthouse", "@@", gbp=fixtures.gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_latest_build_tag_no_builds(self, fixtures: Fixtures) -> None:
        """'@@' for a non-existant machine"""
        with self.assertRaises(SystemExit) as context:
            resolve_build_id("bogus", "@@", gbp=fixtures.gbp)

        self.assertEqual(context.exception.args, ("No builds for bogus",))


class GetMyMachinesFromArgsTestCase(TestCase):
    """Tests for the get_my_machines_from_args method"""

    def test_when_argument_is_none(self):
        args = argparse.Namespace(my_machines=None)

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, [])

    def test_when_argument_is_empty_string(self):
        args = argparse.Namespace(my_machines="")

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, [])

    def test_leading_space(self):
        args = argparse.Namespace(my_machines=" polaris")

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, ["polaris"])

    def test_trailing_space(self):
        args = argparse.Namespace(my_machines="polaris ")

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, ["polaris"])

    def test_multiple_machines(self):
        args = argparse.Namespace(my_machines="polaris lighthouse")

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, ["polaris", "lighthouse"])

    def test_when_argument_does_not_exit(self):
        args = argparse.Namespace()

        machines = get_my_machines_from_args(args)

        self.assertEqual(machines, [])


@given(testkit.environ, testkit.tmpdir)
class LoadEnvTests(TestCase):
    def test_loads_config(self, fixtures: Fixtures) -> None:
        path = fixtures.tmpdir / "config.env"
        path.write_text("TEST=foobar\n")

        status = load_env(path)

        self.assertTrue(status)
        self.assertEqual(os.environ["TEST"], "foobar")

    def test_file_does_not_exist(self, fixtures: Fixtures) -> None:
        path = fixtures.tmpdir / "bogus.env"

        status = load_env(path)

        self.assertFalse(status)

    def test_file_not_readable(self, fixtures: Fixtures) -> None:
        path = fixtures.tmpdir / "unreadable.env"
        path.write_text("TEST=foobar\n")
        path.chmod(0o000)

        status = load_env(path)

        self.assertFalse(status)

    def test_env_variable_override(self, fixtures: Fixtures) -> None:
        path = fixtures.tmpdir / "config.env"
        path.write_text("TEST=foobar\n")

        with mock.patch.dict(os.environ, {"GBPCLI_DONTLOADSERVERENV": "1"}):
            status = load_env(path)

        self.assertFalse(status)
        self.assertTrue("TEST" not in os.environ)


class RePath(TestCase):
    def test(self) -> None:
        orig_path = sys.path.copy()

        try:
            with mock.patch.dict(os.environ, {"PYTHONPATH": "/dev/null"}):
                re_path()
                self.assertEqual(sys.path[0], "/dev/null")
        finally:
            sys.path = orig_path

    def test_when_already_in_path(self) -> None:
        orig_path = sys.path.copy()

        try:
            sys.path.append("/dev/null")
            with mock.patch.dict(os.environ, {"PYTHONPATH": "/dev/null"}):
                re_path()
                self.assertEqual(1, sys.path.count("/dev/null"))
                self.assertEqual(sys.path[-1], "/dev/null")
        finally:
            sys.path = orig_path
