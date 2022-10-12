"""Tests for the inspect subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.inspect import handler as inspect

from . import LOCAL_TIMEZONE, TestCase, load_ndjson


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.inspect.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class InspectTestCase(TestCase):
    """inspect() tests"""

    maxDiff = None

    def test_entire_tree(self):
        args = Namespace(machine=None, tail=0)
        graphql_responses = load_ndjson("inspect.ndjson")
        make_response = self.make_response

        machines_response = next(graphql_responses)
        make_response(machines_response)

        machines_count = len(machines_response["data"]["machines"])
        assert machines_count == 2

        for _ in range(machines_count):
            make_response(next(graphql_responses))

        status = inspect(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), INSPECT_ALL)
        self.assert_graphql(queries.machine_names)
        self.assert_graphql(queries.builds_with_packages, index=1, machine="base")
        self.assert_graphql(queries.builds_with_packages, index=2, machine="gbpbox")

    def test_single_machine(self):
        args = Namespace(machine=["base"], tail=0)
        graphql_responses = load_ndjson("inspect.ndjson", start=4)
        make_response = self.make_response

        response = next(graphql_responses)
        make_response(response)

        status = inspect(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), INSPECT_SINGLE)
        self.assert_graphql(queries.builds_with_packages, machine="base")

    def test_single_machine_with_tail(self):
        args = Namespace(machine=["base"], tail=2)
        graphql_responses = load_ndjson("inspect.ndjson", start=5)
        make_response = self.make_response

        response = next(graphql_responses)
        make_response(response)

        status = inspect(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), INSPECT_SINGLE_WITH_TAIL)
        self.assert_graphql(queries.builds_with_packages, machine="base")


INSPECT_SINGLE_WITH_TAIL = """\
Machines
└── base
    ├── 1 (10/10/22 04:55:19) @first
    │   ├── dev-libs/libpcre-8.45-r1 (05:00:50)
    │   ├── app-crypt/gpgme-1.17.1-r2 (05:01:45)
    │   ├── sys-libs/pam-1.5.2-r2 (05:03:49)
    │   ├── app-crypt/libb2-0.98.1-r2 (05:04:28)
    │   ├── app-portage/portage-utils-0.94.1 (05:05:29)
    │   ├── app-portage/gentoolkit-0.5.1-r1 (05:06:00)
    │   └── net-misc/iputils-20211215 (05:06:03)
    └── 26 (10/11/22 06:03:48) 
        ╭─────────────╮        
        │ Build note. │        
        ╰─────────────╯        
        └── dev-python/pydantic-1.10.2 (06:09:29)
"""
INSPECT_SINGLE = """\
Machines
└── base
    ├── 1 (10/10/22 04:55:19) @first
    │   ├── dev-libs/libpcre-8.45-r1 (05:00:50)
    │   ├── app-crypt/gpgme-1.17.1-r2 (05:01:45)
    │   ├── sys-libs/pam-1.5.2-r2 (05:03:49)
    │   ├── app-crypt/libb2-0.98.1-r2 (05:04:28)
    │   ├── app-portage/portage-utils-0.94.1 (05:05:29)
    │   ├── app-portage/gentoolkit-0.5.1-r1 (05:06:00)
    │   └── net-misc/iputils-20211215 (05:06:03)
    └── 26 (10/11/22 06:03:48) 
        └── dev-python/pydantic-1.10.2 (06:09:29)
"""
INSPECT_ALL = """\
Machines
├── base
│   ├── 1 (10/10/22 04:55:19) @first
│   │   ├── dev-libs/libpcre-8.45-r1 (05:00:50)
│   │   ├── app-crypt/gpgme-1.17.1-r2 (05:01:45)
│   │   ├── sys-libs/pam-1.5.2-r2 (05:03:49)
│   │   ├── app-crypt/libb2-0.98.1-r2 (05:04:28)
│   │   ├── app-portage/portage-utils-0.94.1 (05:05:29)
│   │   ├── app-portage/gentoolkit-0.5.1-r1 (05:06:00)
│   │   └── net-misc/iputils-20211215 (05:06:03)
│   └── 26 (10/11/22 06:03:48) 
│       └── dev-python/pydantic-1.10.2 (06:09:29)
└── gbpbox
    ├── 1 (10/10/22 05:10:09) @first
    │   ├── acct-group/epmd-0-r1 (05:14:27)
    │   ├── acct-group/nginx-0-r1 (05:14:27)
    │   ├── acct-group/rabbitmq-0 (05:14:27)
    │   ├── acct-group/jenkins-0 (05:14:28)
    │   ├── media-fonts/dejavu-2.37 (05:15:02)
    │   ├── acct-group/postgres-0-r1 (05:15:03)
    │   ├── acct-group/nullmail-0 (05:15:05)
    │   ├── dev-libs/libaio-0.3.113 (05:15:10)
    │   ├── app-crypt/libmd-1.0.4 (05:16:07)
    │   ├── dev-lang/go-bootstrap-1.18.6 (05:16:20)
    │   ├── acct-user/nginx-0 (05:16:25)
    │   ├── acct-user/rabbitmq-0 (05:16:35)
    │   ├── dev-libs/lzo-2.10 (05:16:44)
    │   ├── acct-user/epmd-0-r1 (05:16:45)
    │   ├── dev-util/boost-build-1.79.0-r1 (05:16:54)
    │   ├── acct-user/jenkins-0 (05:16:57)
    │   ├── acct-user/postgres-0-r1 (05:16:57)
    │   ├── acct-user/nullmail-0 (05:17:05)
    │   ├── virtual/ttf-fonts-1-r2 (05:17:09)
    │   ├── app-arch/zip-3.0-r4 (05:17:43)
    │   ├── dev-libs/gobject-introspection-common-1.72.0 (05:18:35)
    │   ├── dev-libs/libpcre-8.45-r1 (05:19:19)
    │   ├── media-libs/libpng-1.6.37-r2 (05:19:19)
    │   ├── dev-libs/boost-1.79.0 (05:26:30)
    │   ├── dev-lang/go-1.19.2 (05:27:06)
    │   ├── app-eselect/eselect-fontconfig-20220403 (05:32:38)
    │   ├── app-eselect/eselect-postgresql-2.4 (05:32:38)
    │   ├── dev-go/go-md2man-2.0.0 (05:32:38)
    │   ├── dev-libs/libbsd-0.11.6 (05:32:59)
    │   ├── www-servers/nginx-1.23.1-r1 (05:33:17)
    │   ├── app-crypt/gpgme-1.17.1-r2 (05:33:43)
    │   ├── virtual/perl-Digest-MD5-2.580.0-r1 (05:34:19)
    │   ├── virtual/perl-IO-1.460.0 (05:34:19)
    │   ├── dev-perl/TimeDate-2.330.0-r1 (05:34:31)
    │   ├── virtual/perl-MIME-Base64-3.160.0-r1 (05:34:33)
    │   ├── virtual/perl-Digest-SHA-6.20.0-r3 (05:34:40)
    │   ├── app-containers/runc-1.1.3 (05:34:46)
    │   ├── dev-perl/Mozilla-CA-20999999-r1 (05:34:46)
    │   ├── dev-perl/Error-0.170.290 (05:35:01)
    │   ├── dev-perl/Digest-HMAC-1.40.0 (05:35:09)
    │   ├── dev-perl/Net-SSLeay-1.900.0 (05:35:24)
    │   ├── sys-libs/pam-1.5.2-r2 (05:37:10)
    │   ├── dev-perl/Authen-SASL-2.160.0-r2 (05:37:38)
    │   ├── dev-perl/IO-Socket-SSL-2.72.0 (05:38:01)
    │   ├── x11-libs/xtrans-1.4.0 (05:38:15)
    │   ├── media-libs/freetype-2.12.1-r1 (05:38:16)
    │   ├── virtual/perl-libnet-3.130.0 (05:38:35)
    │   ├── virtual/logger-0-r1 (05:38:45)
    │   ├── sys-block/thin-provisioning-tools-0.9.0-r1 (05:38:53)
    │   ├── app-eselect/eselect-java-0.5.0 (05:39:01)
    │   ├── x11-base/xcb-proto-1.15.2 (05:39:09)
    │   ├── dev-perl/MailTools-2.210.0 (05:39:31)
    │   ├── app-crypt/p11-kit-0.23.22 (05:40:34)
    │   ├── dev-libs/elfutils-0.187 (05:41:01)
    │   ├── sys-libs/binutils-libs-2.38-r2 (05:41:25)
    │   ├── app-crypt/libb2-0.98.1-r2 (05:41:55)
    │   ├── sys-apps/baselayout-java-0.1.0-r1 (05:42:37)
    │   ├── dev-vcs/git-2.35.1 (05:43:23)
    │   ├── sys-fs/lvm2-2.02.188-r3 (05:43:43)
    │   ├── media-libs/fontconfig-2.14.0-r1 (05:44:17)
    │   ├── virtual/libelf-3-r1 (05:44:35)
    │   ├── dev-lang/erlang-24.3.4.2 (05:45:01)
    │   ├── app-portage/portage-utils-0.94.1 (05:45:43)
    │   ├── dev-util/glib-utils-2.72.3 (05:47:37)
    │   ├── app-containers/skopeo-1.5.1 (05:47:58)
    │   ├── media-gfx/graphite2-1.3.14_p20210810-r1 (05:47:59)
    │   ├── mail-mta/nullmailer-2.2-r2 (05:49:16)
    │   ├── net-misc/iputils-20211215 (05:49:43)
    │   ├── dev-db/postgresql-14.5 (05:49:45)
    │   ├── virtual/mta-1-r2 (05:49:58)
    │   ├── dev-lang/elixir-1.12.3 (05:53:39)
    │   ├── x11-base/xorg-proto-2022.1 (05:56:37)
    │   ├── app-containers/buildah-1.27.1 (05:56:53)
    │   ├── x11-libs/pixman-0.40.0 (05:58:24)
    │   ├── dev-python/simplejson-3.17.6 (05:58:50)
    │   ├── app-admin/sudo-1.9.11_p3-r1 (05:59:21)
    │   ├── dev-java/java-config-2.3.1 (05:59:21)
    │   ├── x11-libs/libXau-1.0.9-r1 (05:59:52)
    │   ├── app-portage/gentoolkit-0.5.1-r1 (06:00:33)
    │   ├── x11-libs/libXdmcp-1.1.3-r1 (06:00:33)
    │   ├── dev-libs/glib-2.72.3 (06:02:15)
    │   ├── x11-libs/libxcb-1.15-r1 (06:02:54)
    │   ├── x11-misc/shared-mime-info-2.2 (06:03:42)
    │   ├── x11-misc/compose-tables-1.8.1 (06:04:01)
    │   ├── dev-util/desktop-file-utils-0.26-r2 (06:04:17)
    │   ├── x11-libs/cairo-1.16.0-r6 (06:05:21)
    │   ├── dev-libs/gobject-introspection-1.72.0 (06:05:28)
    │   ├── x11-libs/libX11-1.8.1 (06:05:42)
    │   ├── net-misc/rabbitmq-server-3.8.19-r1 (06:06:05)
    │   ├── media-libs/harfbuzz-5.1.0 (06:07:50)
    │   ├── x11-libs/libXrender-0.9.10-r2 (06:08:27)
    │   ├── x11-libs/libXext-1.3.4 (06:08:34)
    │   ├── x11-libs/libXfixes-6.0.0 (06:09:09)
    │   ├── x11-libs/libXi-1.8 (06:11:06)
    │   ├── x11-libs/libXtst-1.2.3-r2 (06:13:14)
    │   ├── dev-java/openjdk-bin-17.0.3_p7 (06:15:03)
    │   ├── virtual/jdk-17 (06:20:09)
    │   ├── virtual/jre-17 (06:20:20)
    │   └── dev-util/jenkins-bin-2.363 (06:21:16)
    └── 25 (10/11/22 06:03:48) 
        └── dev-python/pydantic-1.10.2 (06:09:34)
"""
