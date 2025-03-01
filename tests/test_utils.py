"""Tests for the "utils" module"""

# pylint: disable=missing-docstring,protected-access,unused-argument
import argparse
import os

from unittest_fixtures import Fixtures, given

from gbpcli.graphql import APIError, check
from gbpcli.types import Build
from gbpcli.utils import get_my_machines_from_args, load_env, resolve_build_id

from . import TestCase, http_response


@given("gbp")
class CheckTestCase(TestCase):
    """check() tests"""

    def test_should_raise_apierror_if_query_response_has_errors(
        self, fixtures: Fixtures
    ):
        error1 = {"message": "The end is near", "locations": [], "path": None}
        error2 = {"message": "Oh no!", "locations": [], "path": None}
        response_with_errors = {"data": {"build": None}, "errors": [error1, error2]}
        gbp = fixtures.gbp
        gbp.query._session.post.return_value = http_response(json=response_with_errors)

        with self.assertRaises(APIError) as context:
            check(gbp.query.gbpcli.machines())

        exception = context.exception
        self.assertEqual(exception.args[0], [error1, error2])
        self.assertEqual(exception.data, {"build": None})


@given("gbp")
class ResolveBuildIdTestCase(TestCase):
    """resolve_build_id() tests"""

    def test_returns_latest_build_for_machine_when_build_id_is_none(
        self, fixtures: Fixtures
    ):
        gbp = fixtures.gbp
        gbp.query._session.post.return_value = http_response(
            json={"data": {"latest": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", None, gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_build_id_is_none_and_no_latest(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        gbp.query._session.post.return_value = http_response(
            json={"data": {"latest": None}}
        )

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", None, gbp=gbp)

        self.assertEqual(context.exception.args, ("No builds for lighthouse",))

    def test_returns_build_when_given_tag(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        gbp.query._session.post.return_value = http_response(
            json={"data": {"resolveBuildTag": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", "@prod", gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_given_tag_that_does_not_exist(self, fixtures: Fixtures):
        gbp = fixtures.gbp
        gbp.query._session.post.return_value = http_response(
            json={"data": {"resolveBuildTag": None}}
        )

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", "@prod", gbp=gbp)

        self.assertEqual(context.exception.args, ("No such tag for lighthouse: prod",))

    def test_returns_build_with_given_id_if_given_build_id_is_numeric(
        self, fixtures: Fixtures
    ):
        gbp = fixtures.gbp

        result = resolve_build_id("lighthouse", "456", gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=456))


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


@given("environ", "tmpdir")
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
