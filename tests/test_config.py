# pylint: disable=missing-docstring
import contextlib
import io
import os.path

from unittest_fixtures import Fixtures, fixture, given

from gbpcli import config

from . import TestCase


@fixture("tmpdir")
def filename(fixtures):
    return os.path.join(fixtures.tmpdir, "gbpcli.toml")


@given("tmpdir", filename)
class ConfigTests(TestCase):
    def test_from_file(self, fixtures: Fixtures) -> None:
        with open(fixtures.filename, "wb+") as fp:
            fp.write(
                b"""\
[gbpcli]
url = "http://test.invalid/"
my_machines = ["babette", "lighthouse"]
"""
            )
            fp.seek(0)
            conf = config.Config.from_file(fp)

        self.assertEqual(conf.url, "http://test.invalid/")
        self.assertEqual(conf.my_machines, ["babette", "lighthouse"])
        self.assertEqual(conf.auth, None)

    def test_from_file_warnings_if_contains_auth_and_readable_by_others(
        self, fixtures: Fixtures
    ):
        with open(fixtures.filename, "wb+") as fp:
            os.chmod(fp.fileno(), 0o666)
            fp.write(
                b"""\
[gbpcli]
auth = { user = "test", api_key = "secret" }
"""
            )
            fp.seek(0)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                config.Config.from_file(fp)

        self.assertEqual(
            stderr.getvalue(),
            "Warning: the config file contains secrets yet is readable by others.\n",
        )

    def test_missing_section(self, fixtures: Fixtures):
        with open(fixtures.filename, "wb+") as fp:
            fp.seek(0)

            with self.assertRaises(config.ConfigError):
                config.Config.from_file(fp)

    def test_empty_section(self, fixtures: Fixtures):
        with open(fixtures.filename, "wb+") as fp:
            fp.write(b"[gbpcli]\n")
            fp.seek(0)

            conf = config.Config.from_file(fp)

        self.assertEqual(conf.url, None)
        self.assertEqual(conf.my_machines, None)
        self.assertEqual(conf.auth, None)


@given("tmpdir", filename)
class IsReadableByOthersTests(TestCase):
    def test_true(self, fixtures: Fixtures) -> None:
        with open(fixtures.filename, "wb+") as fp:
            os.chmod(fp.fileno(), 0o666)
            self.assertTrue(config.is_readable_by_others(fp.fileno()))

    def test_false(self, fixtures: Fixtures) -> None:
        with open(fixtures.filename, "wb+") as fp:
            os.chmod(fp.fileno(), 0o600)
            self.assertFalse(config.is_readable_by_others(fp.fileno()))
