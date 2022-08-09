"""Tests for the "utils" module"""
# pylint: disable=missing-function-docstring
import datetime
import unittest

from gbpcli import APIError, Build
from gbpcli.utils import resolve_build_id, timestr, yesno

from . import make_gbp, make_response, mock_print


class UtilsTestCase(unittest.TestCase):
    """Tests for the yesno() function"""

    def test_true(self):
        self.assertEqual("yes", yesno(True))

    def test_false(self):
        self.assertEqual("no", yesno(False))


class TimestrTestCase(unittest.TestCase):
    """timestr() tests"""

    def test(self):
        timestamp = datetime.datetime.fromisoformat("2021-07-20T16:45:06.445500+00:00")
        timezone = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")

        self.assertEqual(timestr(timestamp, timezone), "Tue Jul 20 09:45:06 2021 -0700")


class CheckTestCase(unittest.TestCase):
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


class ResolveBuildIdTestCase(unittest.TestCase):
    """resolve_build_id() tests"""

    def test_returns_latest_build_for_machine_when_build_id_is_none(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"latest": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", None, gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    @mock_print("gbpcli.utils")
    def test_aborts_when_build_id_is_none_and_no_latest(self, print_mock):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json={"data": {"latest": None}})

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", None, gbp=gbp)

        self.assertEqual(context.exception.args, (1,))
        self.assertEqual(print_mock.stderr.getvalue(), "No builds for lighthouse\n")

    def test_returns_build_when_given_tag(self):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"resolveBuildTag": {"id": "lighthouse.123"}}}
        )

        result = resolve_build_id("lighthouse", "@prod", gbp=gbp)

        self.assertEqual(result, Build(machine="lighthouse", number=123))

    @mock_print("gbpcli.utils")
    def test_aborts_when_given_tag_that_does_not_exist(self, print_mock):
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json={"data": {"resolveBuildTag": None}}
        )

        with self.assertRaises(SystemExit) as context:
            resolve_build_id("lighthouse", "@prod", gbp=gbp)

        self.assertEqual(context.exception.args, (1,))
        self.assertEqual(
            print_mock.stderr.getvalue(), "No such tag for lighthouse: prod\n"
        )

    def test_returns_build_with_given_id_if_given_build_id_is_numeric(self):
        gbp = make_gbp()

        result = resolve_build_id("lighthouse", "456", gbp)

        self.assertEqual(result, Build("lighthouse", 456))

    def test_raises_valueerror_when_abort_on_error_is_false_and_bad_id(self):
        gbp = make_gbp()

        with self.assertRaises(ValueError) as context:
            resolve_build_id("lighthouse", "bogus", gbp, abort_on_error=False)

        self.assertEqual(context.exception.args, ("Invalid build ID: bogus",))
