"""Run tests for gbpcli"""

import argparse
import os
import unittest


def main() -> None:
    """Program entry point"""
    args = parse_args()
    os.environ["DJANGO_SETTINGS_MODULE"] = args.settings

    # These values are required in order to import the publisher module
    os.environ.setdefault("BUILD_PUBLISHER_JENKINS_BASE_URL", "http://jenkins.invalid/")
    os.environ.setdefault("BUILD_PUBLISHER_STORAGE_PATH", "__testing__")

    loader = unittest.TestLoader()
    loader.testNamePatterns = [f"*{pattern}*" for pattern in args.tests] or None
    tests = loader.discover("")
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=args.failfast)
    test_result = runner.run(tests)

    raise SystemExit(int(not test_result.wasSuccessful()))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    default_settings = os.environ.get("DJANGO_SETTINGS_MODULE", "gbp_testkit.settings")
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", default=default_settings)
    parser.add_argument("-f", "--failfast", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("tests", nargs="*", default=[])

    return parser.parse_args()


if __name__ == "__main__":
    main()
