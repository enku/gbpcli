"""Tests for the "utils" module"""
# pylint: disable=missing-function-docstring
import argparse
import datetime

from gbpcli import APIError, Build
from gbpcli.utils import (
    format_machine,
    get_my_machines_from_args,
    resolve_build_id,
    timestr,
    yesno,
)

from . import TestCase, make_gbp, make_response


class UtilsTestCase(TestCase):
    """Tests for the yesno() function"""

    def test_true(self):
        self.assertEqual("yes", yesno(True))

    def test_false(self):
        self.assertEqual("no", yesno(False))


class TimestrTestCase(TestCase):
    """timestr() tests"""

    def test(self):
        timestamp = datetime.datetime.fromisoformat("2021-07-20T16:45:06.445500+00:00")
        timezone = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")

        self.assertEqual(timestr(timestamp, timezone), "Tue Jul 20 09:45:06 2021 -0700")


class CheckTestCase(TestCase):
    """check() tests"""

    def test_should_raise_apierror_if_query_response_has_errors(self):
        error1 = {"message": "The end is near", "locations": [], "path": None}
        error2 = {"message": "Oh no!", "locations": [], "path": None}
        response_with_errors = {"data": {"build": None}, "errors": [error1, error2]}
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=response_with_errors)

        with self.assertRaises(APIError) as context:
            gbp.check("{ foo { bar } }")

        exception = context.exception
        self.assertEqual(exception.args[0], [error1, error2])
        self.assertEqual(exception.data, {"build": None})


class ResolveBuildIdTestCase(TestCase):
    """resolve_build_id() tests"""

    def test_returns_latest_build_for_machine_when_build_id_is_none(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"latest": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", None, gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_build_id_is_none_and_no_latest(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json={"data": {"latest": None}})

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", None, gbp=gbp, errorf=self.errorf)

        self.assertEqual(context.exception.args, (1,))
        self.assertEqual(self.errorf.getvalue(), "No builds for lighthouse\n")

    def test_returns_build_when_given_tag(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"resolveBuildTag": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", "@prod", gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    def test_aborts_when_given_tag_that_does_not_exist(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"resolveBuildTag": None}}
        )

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", "@prod", gbp=gbp, errorf=self.errorf)

        self.assertEqual(context.exception.args, (1,))
        self.assertEqual(self.errorf.getvalue(), "No such tag for lighthouse: prod\n")

    def test_returns_build_with_given_id_if_given_build_id_is_numeric(self):
        gbp = make_gbp()

        result = resolve_build_id("lighthouse", "456", gbp)

        self.assertEqual(result, Build("lighthouse", 456))

    def test_raises_valueerror_when_abort_on_error_is_false_and_bad_id(self):
        gbp = make_gbp()

        with self.assertRaises(ValueError) as context:
            resolve_build_id("lighthouse", "bogus", gbp, abort_on_error=False)

        self.assertEqual(context.exception.args, ("Invalid build ID: bogus",))


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


class FormatMachineTest(TestCase):
    """Test for the format_machines method"""

    def test_when_machine_is_mymachine(self):
        machine = "polaris"
        args = argparse.Namespace(my_machines="polaris")

        formatted = format_machine(machine, args)

        expected = "[machine][mymachine]polaris[/mymachine][/machine]"
        self.assertEqual(formatted, expected)

    def test_when_machine_is_not_mymachine(self):
        machine = "polaris"
        args = argparse.Namespace(my_machines="lighthouse babette")

        formatted = format_machine(machine, args)

        expected = "[machine]polaris[/machine]"
        self.assertEqual(formatted, expected)
