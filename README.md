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
usage: gbp [-h] [--url URL]
           {build,diff,keep,latest,list,logs,machines,notes,packages,publish,pull,status} ...

positional arguments:
  {build,diff,keep,latest,list,logs,machines,notes,packages,publish,pull,status}

options:
  -h, --help            show this help message and exit
  --url URL             GBP url
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.

To list the machines which have builds:

```bash
$ gbp machines
         Machines         
╭───────────────┬────────╮
│ Name          │ Builds │
├───────────────┼────────┤
│ babette       │     10 │
│ blackwidow    │     45 │
│ gbp           │     45 │
│ jenkins       │      8 │
│ lighthouse    │     43 │
│ pgadmin       │      7 │
│ postgres      │      8 │
│ rabbitmq      │      8 │
│ teamplayer    │      2 │
│ testing       │     43 │
╰───────────────┴────────╯
```

To list the available builds for a given machine:

```bash
$ gbp list babette
                   💻 babette                   
╭────────┬─────┬───────────────────┬────────╮
│ Status │  ID │ Submitted         │ Tags   │
├────────┼─────┼───────────────────┼────────┤
│  K     │ 104 │ 04/25/21 08:51:19 │ @first │
│        │ 132 │ 05/21/21 13:27:50 │        │
│ *      │ 412 │ 02/27/22 06:42:08 │        │
│ *      │ 413 │ 02/28/22 06:43:32 │        │
│ *      │ 430 │ 03/16/22 08:49:15 │        │
│ *      │ 431 │ 03/17/22 08:54:43 │        │
│ *      │ 434 │ 03/21/22 16:37:30 │        │
│ *      │ 435 │ 03/22/22 12:01:48 │        │
│ * PN   │ 437 │ 03/22/22 13:28:13 │        │
│ *      │ 438 │ 03/23/22 13:09:26 │        │
╰────────┴─────┴───────────────────┴────────╯
```

In the above example, the `P` output for build `437` signifies that this build
is currently published (`P`) and there is a user note for that build (`N`).
The `*` means that the respective build has new binary packages. The `K` for
build `104` means that the build is marked for keeping and will not be removed
during the purge process. Build `104` has also been given a "first" tag.

```bash
$ gbp status babette 412
╭────────────────────────────────────────────────╮
│ Build:          babette/412                    │
│ BuildDate:      Sun Feb 27 06:38:30 2022 -0500 │
│ Submitted:      Sun Feb 27 06:42:08 2022 -0500 │
│ Completed:      Sun Feb 27 06:45:00 2022 -0500 │
│ Published:      no                             │
│ Keep:           no                             │
│ Packages-built:                                │
│                 app-text/opensp-1.5.2-r7       │
╰────────────────────────────────────────────────╯

╭─────────────────────╮
│📎 Notes             │
├─────────────────────┤
│This is a build note.│
╰─────────────────────╯
```

Edit/delete build notes using the `gbp notes` command.


The `status` subcommand displays metadata about a given build.  If the build
number is not given, it defaults to the latest build for that machine.

The `diff` subcommand display differences between two build.

```bash
$ gbp diff babette 437 438
diff -r babette/437 babette/438
--- a/babette/437 Tue Mar 22 13:28:13 2022 -0500
+++ b/babette/438 Wed Mar 23 13:09:26 2022 -0500
-app-admin/sudo-1.9.8_p2-1
+app-admin/sudo-1.9.8_p2-r1-1
-app-crypt/gnupg-2.2.34-1
+app-crypt/gnupg-2.2.34-r1-1
-dev-python/importlib_metadata-4.11.2-1
-dev-python/zipp-3.7.0-r1-1
-net-misc/curl-7.79.1-3
+net-misc/curl-7.79.1-r1-1
```
If the second build number is not given, it defaults to the latest build for
that machine.  If the first build number is not given, it defaults to the
published build for that machine.

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish babette 438
```

If the build nubmer is not given, it defaults to the latest build for that machine.

The `build` subcommand can schedule a build in CI/CD for the given machine,
e.g.:

```bash
$ gbp build babette
```
