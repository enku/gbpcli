"""Tests for the graphql module"""

# pylint: disable=missing-docstring
from unittest import mock

import requests
from yarl import URL

from gbpcli import graphql

from . import TestCase, http_response


class QueryTestCase(TestCase):
    def test_passes_given_query_and_vars_to_graphql_request(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        variables = {"name": "value"}

        query(**variables)

        session.post.assert_called_once_with(
            "https://gbp.invalid",
            json={"query": "query foo { bar }", "variables": {"name": "value"}},
        )

    def test_raises_when_http_response_is_an_error(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        session.post.return_value = http_response(status_code=404)

        with self.assertRaises(requests.exceptions.HTTPError):
            query()

    def test_returns_graphql_data_and_errors(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        data_and_errors = {"data": {"foo": "bar"}, "errors": [{"this": "that"}]}
        session.post.return_value = http_response(json=data_and_errors)

        response = query()

        self.assertEqual(response, ({"foo": "bar"}, [{"this": "that"}]))


class QueriesTestCase(TestCase):
    """Tests for the Queries wrapper"""

    def test_returns_query_on_attribute_access(self):
        queries = graphql.Queries(URL("https://gbp.invalid"))

        logs_query = queries.gbpcli.logs

        self.assertEqual(
            logs_query.query,
            "query ($id: ID!) {\n  build(id: $id) {\n    logs\n  }\n}\n",
        )

    def test_raises_attribute_error_when_file_not_found(self):
        queries = graphql.Queries(URL("https://gbp.invalid"))

        with self.assertRaises(AttributeError):
            print(queries.gbpcli.bogus)

    def test_raises_attribute_error_when_distribution_not_found(self):
        queries = graphql.Queries(URL("https://gbp.invalid"))

        with self.assertRaises(AttributeError):
            print(queries.bogus)

    def test_to_dict_returns_dict(self):
        queries = graphql.Queries(URL("https://gbp.invalid"))

        as_dict = queries.gbpcli.to_dict()

        self.assertIsInstance(as_dict, dict)
        self.assertIn("logs", as_dict)

    def test_adds_auth_header_to_session(self):
        # pylint: disable=protected-access
        auth = {"user": "test", "api_key": "secret"}
        queries = graphql.Queries(URL("https://gbp.invalid"), auth=auth)

        expected = f'Basic {graphql.auth_encode("test", "secret")}'
        self.assertEqual(queries._session.headers["Authorization"], expected)


class AuthEncodeTests(TestCase):
    def test(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization#basic_authentication
        user = "aladdin"
        key = "opensesame"

        value = graphql.auth_encode(user, key)

        self.assertEqual(value, "YWxhZGRpbjpvcGVuc2VzYW1l")
