"""Tests for the list subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.list import handler as list_command

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.subcommands.list.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class ListTestCase(unittest.TestCase):
    """list() tests"""

    @mock_print("gbpcli.subcommands.list")
    def test(self, print_mock):
        args = Namespace(machine="lighthouse")
        mock_json = parse(load_data("list.json"))
        gbp = make_gbp()
        gbp.session.get.return_value = make_response(json=mock_json)

        status = list_command(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), EXPECTED_OUTPUT)
        gbp.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/"
        )


EXPECTED_OUTPUT = """\
[K N]   237 04/25/21 16:10:22
[K N]   638 05/14/21 06:21:21
[   ]  1060 05/31/21 23:12:12
[   ]  1604 06/27/21 10:28:03
[   ]  1644 06/30/21 23:18:17
[K N]  1804 07/08/21 20:09:52
[   ]  1923 07/13/21 23:20:47
[   ]  1946 07/14/21 23:23:35
[K N]  1959 07/15/21 12:21:02
[   ]  1970 07/15/21 23:26:36
[   ]  1993 07/16/21 23:27:36
[   ]  2016 07/17/21 23:41:20
[   ]  2042 07/18/21 23:23:27
[   ]  2043 07/19/21 00:18:26
[  N]  2044 07/19/21 01:40:58
[  N]  2045 07/19/21 02:46:20
[   ]  2046 07/19/21 03:30:36
[  N]  2047 07/19/21 04:44:11
[   ]  2048 07/19/21 05:16:04
[  N]  2049 07/19/21 05:53:03
[  N]  2050 07/19/21 06:32:08
[  N]  2051 07/19/21 07:26:48
[   ]  2052 07/19/21 08:16:03
[   ]  2053 07/19/21 09:18:56
[   ]  2054 07/19/21 10:15:36
[   ]  2055 07/19/21 11:13:43
[  N]  2056 07/19/21 12:17:17
[   ]  2057 07/19/21 13:16:04
[  N]  2058 07/19/21 13:49:23
[  N]  2059 07/19/21 14:17:58
[  N]  2060 07/19/21 15:23:42
[   ]  2061 07/19/21 16:16:33
[   ]  2062 07/19/21 17:17:01
[   ]  2063 07/19/21 18:16:36
[   ]  2064 07/19/21 19:19:44
[  N]  2065 07/20/21 00:01:35
[   ]  2066 07/20/21 00:19:23
[   ]  2067 07/20/21 01:24:24
[   ]  2068 07/20/21 01:49:47
[   ]  2069 07/20/21 02:35:00
[   ]  2070 07/20/21 03:26:31
[   ]  2071 07/20/21 04:37:35
[   ]  2072 07/20/21 05:27:02
[   ]  2073 07/20/21 06:16:41
[   ]  2074 07/20/21 08:25:29
[   ]  2075 07/20/21 09:08:22
[  N]  2076 07/20/21 09:39:46
[   ]  2077 07/20/21 10:31:51
[   ]  2078 07/20/21 11:28:26
[   ]  2079 07/20/21 12:25:33
[ PN]  2080 07/20/21 14:39:45
[   ]  2081 07/20/21 15:19:39
[   ]  2082 07/20/21 16:23:43
[   ]  2083 07/20/21 17:22:03
[  N]  2084 07/20/21 18:27:18
[   ]  2085 07/20/21 19:21:41
[  N]  2086 07/20/21 20:23:27
"""
