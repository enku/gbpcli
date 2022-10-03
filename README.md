# CLI for Gentoo Build Publisher

<div align="center">

[![asciicast](https://asciinema.org/a/8oqcjBoC6Miy2MJlqb8gm1UwY.svg)](https://asciinema.org/a/8oqcjBoC6Miy2MJlqb8gm1UwY)

</div>

## Introduction

This is a command-line interface for [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher), a system that
combines Gentoo Linux and CI/CD so that updating a Gentoo predictable and
consistent.

This is a pip-installable Python package:

```bash
$ pip install gbpcli
```

## Usage

The full command set supported:

```bash
usage: gbp [-h] [--version] [--url URL] [--color WHEN]
           {build,diff,keep,latest,list,logs,machines,notes,packages,publish,pull,status,tag} ...

positional arguments:
  {build,diff,keep,latest,list,logs,machines,notes,packages,publish,pull,status,tag}

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --url URL             GBP url
  --color WHEN          color output
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.

To list the machines which have builds:

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_machines.png](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_machines.png)

The "Latest" column shows the latest build ID for the given machine. If the ID has a `*`
beside it that denotes that the latest build is published (available for emerges).

To list the available builds for a given machine:

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_list.png](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_list.png)

In the above example, the `P` output for build `623` signifies that this build
is currently published.  The `*` flag means that the respective build has new
binary packages. The `K` for build `104` means that the build is marked for
keeping and will not be removed during the purge process. Build `600` has also
been given a "stable" tag.  The `N` flag for build `631` means that the build
has a note attached.

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_status.png](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_status.png)

Edit/delete build notes using the `gbp notes` command.


The `status` subcommand displays metadata about a given build.  If the build
number is not given, it defaults to the latest build for that machine.

The `diff` subcommand display differences between two build.

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_diff.png](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_diff.png)

If the second build number is not given, it defaults to the latest build for
that machine.  If the first build number is not given, it defaults to the
published build for that machine.

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish babette 631
```

If the build nubmer is not given, it defaults to the latest build for that machine.

The `build` subcommand can schedule a build in CI/CD for the given machine,
e.g.:

```bash
$ gbp build babette
```
