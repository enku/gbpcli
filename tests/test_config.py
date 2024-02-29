# pylint: disable=missing-docstring
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
        self.assertEqual(conf.api_key, None)

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
        self.assertEqual(conf.api_key, None)
