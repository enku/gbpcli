"""Tests for the GBP interface"""
# pylint: disable=missing-docstring
import requests.exceptions

from gbpcli import DEFAULT_THEME, Queries, get_colormap_from_string

from . import TestCase, make_response, mock_print


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

    @mock_print("gbpcli")
    def test_exits_on_connection_errors(self, _):
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


class QueriesTestCase(TestCase):
    """Tests for the Queries wrapper"""

    def test_returns_query_on_attribute_access(self):
        queries = Queries()

        logs_query = queries.logs

        self.assertEqual(
            logs_query, "query ($id: ID!) {\n  build(id: $id) {\n    logs\n  }\n}\n"
        )

    def test_raises_attribute_error_when_file_not_found(self):
        queries = Queries()

        with self.assertRaises(AttributeError):
            queries.bogus  # pylint: disable=pointless-statement

    def test_to_dict_returns_dict(self):
        queries = Queries()

        as_dict = queries.to_dict()

        self.assertIsInstance(as_dict, dict)
        self.assertIn("logs", as_dict)


class GetColormapFromString(TestCase):
    """Tests for the get_colormap_from_string function"""

    def test_empty_string(self):
        result = get_colormap_from_string("")

        self.assertEqual(result, DEFAULT_THEME)

    def test_double_colons(self):
        string = "header=test_header:note=test_note::build_id=test_build_id"
        #                                          ^^
        result = get_colormap_from_string(string)

        self.assertEqual(result["header"], "test_header")
        self.assertEqual(result["note"], "test_note")
        self.assertEqual(result["build_id"], "test_build_id")

    def test_double_equals(self):
        string = "header=blue:notes==white:build_id=bold"
        #                          ^^

        with self.assertRaises(ValueError) as context:
            get_colormap_from_string(string)

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'header=blue:notes==white:build_id=bold'",
        )

    def test_missing_equals(self):
        string = "header=test_header:note:build_id=test_build_id"
        #                                ^

        with self.assertRaises(ValueError) as context:
            get_colormap_from_string(string)

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'header=test_header:note:build_id=test_build_id'",
        )

    def test_only_colons(self):
        result = get_colormap_from_string("::::::::::")

        self.assertEqual(result, DEFAULT_THEME)

    def test_garbage_input(self):
        with self.assertRaises(ValueError) as context:
            get_colormap_from_string("This is totally garbage!")

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'This is totally garbage!'",
        )

    def test_ignores_unknown_names(self):
        string = "header=test_header:note=test_note:unknown=test_unknown"

        result = get_colormap_from_string(string)

        self.assertEqual(result["header"], "test_header")
        self.assertEqual(result["note"], "test_note")
        self.assertFalse("unknown" in result)
