# pylint: disable=missing-docstring
import contextlib
import io
import os.path

from gbpcli import config

from . import TestCase, tempdir_test


class ConfigTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.tempdir = tempdir_test(self)
        self.filename = os.path.join(self.tempdir, "gbpcli.toml")

    def test_from_file(self) -> None:
        with open(self.filename, "wb+") as fp:
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

    def test_from_file_warnings_if_contains_auth_and_readable_by_others(self):
        with open(self.filename, "wb+") as fp:
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

    def test_missing_section(self):
        with open(self.filename, "wb+") as fp:
            fp.seek(0)

            with self.assertRaises(config.ConfigError):
                config.Config.from_file(fp)

    def test_empty_section(self):
        with open(self.filename, "wb+") as fp:
            fp.write(b"[gbpcli]\n")
            fp.seek(0)

            conf = config.Config.from_file(fp)

        self.assertEqual(conf.url, None)
        self.assertEqual(conf.my_machines, None)
        self.assertEqual(conf.auth, None)


class IsReadableByOthersTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.tempdir = tempdir_test(self)
        self.filename = os.path.join(self.tempdir, "gbpcli.toml")

    def test_true(self) -> None:
        with open(self.filename, "wb+") as fp:
            os.chmod(fp.fileno(), 0o666)
            self.assertTrue(config.is_readable_by_others(fp.fileno()))

    def test_false(self) -> None:
        with open(self.filename, "wb+") as fp:
            os.chmod(fp.fileno(), 0o600)
            self.assertFalse(config.is_readable_by_others(fp.fileno()))
