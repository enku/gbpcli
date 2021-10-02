"""Tests for the "utils" module"""
# pylint: disable=missing-function-docstring
import datetime
import unittest

from gbpcli import APIError
from gbpcli.utils import timestr, yesno

from . import make_gbp, make_response


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
