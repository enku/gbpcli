# CLI for Gentoo Build Publisher

## Introduction

This is a command-line interface for [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher), a system that
combines Gentoo Linux and CI/CD so that updating a Gentoo predictable and
consistent.

This is a pip-installable Python package:

```bash
$ pip install git+https://github.com/enku/gbpcli.git
```

## Usage

The full command set supported:

```bash
$ gbp --help
usage: gbp [-h] [--url URL] {diff,latest,list,logs,machines,publish,show} ...

positional arguments:
  {diff,latest,list,logs,machines,publish,show}

optional arguments:
  -h, --help            show this help message and exit
  --url URL             GBP url
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.

To list the machines which have builds:

```bash
$ gbp machines
babette          14
blackwidow       45
gbp              45
jenkins           8
lighthouse       43
pgadmin           7
postgres          8
rabbitmq          8
teamplayer        2
testing          43
```

To list the available builds for a given machine:

```bash
$ gbp list babette
[K  ]   104 04/25/21 06:51:19
[   ]   109 04/30/21 07:27:04
[K N]   132 05/21/21 11:27:50
[ PN]   157 06/16/21 08:10:04
[   ]   167 06/27/21 08:02:12
[  N]   169 06/30/21 06:38:53
[  N]   187 07/17/21 10:20:25
[  N]   188 07/18/21 13:32:48
```

In the above example, the `PN` output for build `157` signifies that this build
is currently published (`P`) and there is a user note for that build (`N`).

```bash
$ gbp show babette 188
Build: babette/188
Submitted: Sun Jul 18 13:32:48 2021 -0700
Completed: Sun Jul 18 13:35:04 2021 -0700
Published: no
Keep: no

    Packages built:

    * app-misc/pax-utils-1.3.2-1
    * app-text/po4a-0.57-r1-1
    * sys-apps/util-linux-2.36.2-r1-1
    * sys-devel/gcc-10.3.0-r2-1
    * sys-libs/readline-8.1_p1-r1-1
    * sys-process/procps-3.3.17-r1-1
```


The `show` subcommand displays metadata about a given build.  If the build
number is not given, it defaults to the latest build for that machine.

The `diff` subcommand display differences between two build.

```bash
$ gbp diff babette 187 188
diff -r babette/187 babette/188
--- a/babette/187 Sat Jul 17 10:20:25 2021 -0700
+++ b/babette/188 Sun Jul 18 13:32:48 2021 -0700
-app-misc/pax-utils-1.3.1-2
+app-misc/pax-utils-1.3.2-1
-app-text/po4a-0.57-1
+app-text/po4a-0.57-r1-1
-sys-apps/util-linux-2.36.2-2
+sys-apps/util-linux-2.36.2-r1-1
-sys-devel/gcc-10.3.0-r1-1
+sys-devel/gcc-10.3.0-r2-1
-sys-libs/readline-8.1_p1-1
+sys-libs/readline-8.1_p1-r1-1
+sys-process/procps-3.3.17-r1-1
```
If the second build number is not given, it defaults to the latest build for
that machine.  If the first build number is not given, it defaults to the
published build for that machine.

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish babette 188
```

If the build nubmer is not given, it defaults to the latest build for that machine.
