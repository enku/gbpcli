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
usage: gbp [-h] [--url URL] {build,diff,latest,list,logs,machines,publish,show} ...

positional arguments:
  {build,diff,latest,list,logs,machines,publish,show}

options:
  -h, --help            show this help message and exit
  --url URL             GBP url
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.

To list the machines which have builds:

```bash
$ gbp machines
babette          10
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
[*  N]   293 11/03/21 18:56:03
[    ]   294 11/04/21 18:56:02
[*  N]   295 11/05/21 18:58:42
[*  N]   296 11/06/21 20:36:07
[*  N]   297 11/07/21 20:07:58
[    ]   298 11/08/21 18:56:19
[*  N]   299 11/09/21 18:56:54
[    ]   300 11/10/21 18:56:25
[*  N]   301 11/11/21 21:04:31
[  PN]   302 11/12/21 20:33:33
```

In the above example, the `PN` output for build `302` signifies that this
build is currently published (`P`) and there is a user note for that build
(`N`).  The `*` means that the respective build has new binary packages.

```bash
$ gbp show babette 301
Build: babette/301
Submitted: Thu Nov 11 21:04:31 2021 -0600
Completed: Thu Nov 11 21:08:20 2021 -0600
Published: no
Keep: no

    The glibc update seems wonky here. I submitted a bug report.
```

Edit/delete build notes using the `gbp notes` command.


The `show` subcommand displays metadata about a given build.  If the build
number is not given, it defaults to the latest build for that machine.

The `diff` subcommand display differences between two build.

```bash
$ gbp diff babette 298 299
diff -r babette/298 babette/299
--- a/babette/298 Mon Nov  8 18:56:19 2021 -0600
+++ b/babette/299 Tue Nov  9 18:56:54 2021 -0600
-dev-perl/Locale-gettext-1.70.0-2
+dev-perl/Locale-gettext-1.70.0-r1-1
```
If the second build number is not given, it defaults to the latest build for
that machine.  If the first build number is not given, it defaults to the
published build for that machine.

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish babette 302
```

If the build nubmer is not given, it defaults to the latest build for that machine.

The `build` subcommand can schedule a build in CI/CD for the given machine,
e.g.:

```bash
$ gbp build babette
```
