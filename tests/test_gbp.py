"""Tests for the GBP interface"""

# pylint: disable=missing-docstring,protected-access
import os
from unittest import mock

import requests.exceptions

from gbpcli import GBP, build_parser, config

from . import TestCase, tempdir_test


class GGPTestCase(TestCase):
    def test_search_notes_deprecation(self):
        self.make_response("search_notes.json")

        with self.assertWarns(DeprecationWarning) as context:
            self.gbp.search_notes("lighthouse", "test")

        self.assertEqual(
            context.warning.args[0], "This method is deprecated. Use search() instead"
        )

    def test_url(self) -> None:
        gbp = GBP("http://gbp.invalid/")

        self.assertEqual(gbp.query._url, "http://gbp.invalid/graphql")


class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_does_not_exit_when_flag_turned_off(self):
        self.gbp.exit_gracefully_on_requests_errors = False
        error = requests.exceptions.ConnectionError()
        self.gbp.query._session.post.side_effect = error

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            self.gbp.query.gbpcli.machines()

        self.assertIs(cxt.exception, error)


class BuildParserTestCase(TestCase):
    """Tests for the build_parser method"""

    def setUp(self):
        super().setUp()

        patch = mock.patch.dict(os.environ, clear=True)
        self.addCleanup(patch.stop)
        patch.start()

        tmpdir = tempdir_test(self)
        patch = mock.patch("gbpcli.platformdirs.user_config_dir")
        self.addCleanup(patch.stop)
        patched = patch.start()
        patched.return_value = tmpdir

        self.parser = build_parser(config.Config())

    def test_my_machines_string(self):
        argv = ["--my-machines", "this that the other"]

        args = self.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")

    def test_my_machines_not_passed(self):
        argv = []

        args = self.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "")

    def test_my_machines_from_environ(self):
        os.environ["GBPCLI_MYMACHINES"] = "this that the other"
        argv = []

        parser = build_parser(config.Config())
        args = parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")
