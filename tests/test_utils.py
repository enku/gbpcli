"""Tests for the "utils" module"""
# pylint: disable=missing-function-docstring
import datetime
import unittest
from unittest import mock

from gbpcli import GBP, APIError, NotFound, UnexpectedResponseError
from gbpcli.utils import timestr, yesno

from . import make_response

# moved to GBP as a static method
check = GBP.check


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

    def test_should_raise_notfound_when_404_response(self):
        response_mock = mock.Mock(status_code=404)

        with self.assertRaises(NotFound):
            check(response_mock)

    def test_should_return_response_json_if_is_json_true(self):
        json_response = {"error": None, "foo": "bar"}
        response_mock = make_response(json=json_response)

        value = check(response_mock)

        self.assertEqual(value, json_response)

    def test_should_error_if_json_has_error(self):
        json_response = {"error": "Something is wrong"}
        response_mock = make_response(json=json_response)

        with self.assertRaises(APIError):
            check(response_mock)

    def test_should_error_if_response_not_json(self):
        response_mock = make_response(status_code=204, content=b"")

        with self.assertRaises(UnexpectedResponseError):
            check(response_mock)

    def test_should_return_raw_response_when_is_json_false(self):
        response_mock = make_response(content=b"test")

        value = check(response_mock, is_json=False)

        self.assertEqual(value, b"test")
