"""Tests for the GBP interface"""
# pylint: disable=missing-docstring
import requests.exceptions

from . import TestCase, make_response


class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_passes_given_query_and_vars_to_graphql_request(self):
        query = "query foo { bar }"
        variables = {"name": "value"}

        self.gbp.query(query, variables)

        self.assert_graphql(query, name="value")

    def test_raises_when_http_response_is_an_error(self):
        query = "query foo { bar }"
        response = make_response(status_code=404)
        self.gbp.session.post.return_value = response

        with self.assertRaises(requests.exceptions.HTTPError):
            self.gbp.query(query)

    def test_returns_graphql_data_and_errors(self):
        query = "query foo { bar }"
        data_and_errors = {"data": {"foo": "bar"}, "errors": [{"this": "that"}]}
        self.make_response(data_and_errors)

        response = self.gbp.query(query)

        self.assertEqual(response, ({"foo": "bar"}, [{"this": "that"}]))

    def test_exits_on_connection_errors(self):
        query = "query foo { bar }"
        self.gbp.session.post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(SystemExit) as cxt:
            self.gbp.query(query)

        exception = cxt.exception
        self.assertEqual(exception.args, (-1,))

    def test_does_not_exit_when_flag_turned_off(self):
        self.gbp.exit_gracefully_on_requests_errors = False
        error = requests.exceptions.ConnectionError()
        self.gbp.session.post.side_effect = error
        query = "query foo { bar }"

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            self.gbp.query(query)

        self.assertIs(cxt.exception, error)
