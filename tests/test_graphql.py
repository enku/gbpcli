"""Tests for the graphql module"""
# pylint: disable=missing-docstring
import unittest
from unittest import mock

import requests
from yarl import URL

from gbpcli import graphql

from . import make_response


class QueryTestCase(unittest.TestCase):
    def test_passes_given_query_and_vars_to_graphql_request(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        variables = {"name": "value"}

        query(**variables)

        session.post.assert_called_once_with(
            "https://gbp.invalid",
            json={"query": "query foo { bar }", "variables": {"name": "value"}},
            headers=graphql.Query.headers,
        )

    def test_raises_when_http_response_is_an_error(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        session.post.return_value = make_response(status_code=404)

        with self.assertRaises(requests.exceptions.HTTPError):
            query()

    def test_returns_graphql_data_and_errors(self):
        session = mock.Mock(spec=requests.Session)
        query = graphql.Query("query foo { bar }", "https://gbp.invalid", session)
        data_and_errors = {"data": {"foo": "bar"}, "errors": [{"this": "that"}]}
        session.post.return_value = make_response(json=data_and_errors)

        response = query()

        self.assertEqual(response, ({"foo": "bar"}, [{"this": "that"}]))


class QueriesTestCase(unittest.TestCase):
    """Tests for the Queries wrapper"""

    def test_returns_query_on_attribute_access(self):
        queries = graphql.Queries(URL("https://gbp.invalid"), "gbpcli")

        logs_query = queries.logs

        self.assertEqual(
            logs_query.query,
            "query ($id: ID!) {\n  build(id: $id) {\n    logs\n  }\n}\n",
        )

    def test_raises_attribute_error_when_file_not_found(self):
        queries = graphql.Queries(URL("https://gbp.invalid"), "gbpcli")

        with self.assertRaises(AttributeError):
            print(queries.bogus)

    def test_to_dict_returns_dict(self):
        queries = graphql.Queries(URL("https://gbp.invalid"), "gbpcli")

        as_dict = queries.to_dict()

        self.assertIsInstance(as_dict, dict)
        self.assertIn("logs", as_dict)
