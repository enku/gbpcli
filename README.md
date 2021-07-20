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
    diff                Show differences between two builds
    latest              Show the latest build number for the given machine
    list                List builds for the given machines
    logs                Display logs for the given build
    machines            List machines with builds
    publish             Publish a build
    show                Show details for a given build

optional arguments:
  -h, --help            show this help message and exit
  --url URL             GBP url
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.


To list the available builds for a given machine:

```bash
$ gbp list babette
[K  ]   104 04/25/21 06:51:19
[   ]   109 04/30/21 07:27:04
[K N]   132 05/21/21 11:27:50
[ PN]   157 06/16/21 08:10:04
[   ]   167 06/27/21 08:02:12
[   ]   168 06/29/21 11:00:41
[  N]   169 06/30/21 06:38:53
[  N]   170 07/01/21 06:52:48
[   ]   171 07/02/21 06:34:30
```

In the above example, the `PN` output for build `157` signifies that this build
is currently published (`P`) and there is a user note for that build (`N`).

```bash
gbp show babette 172
Build: babette/172
Submitted: Sat Jul  3 06:31:58 2021 -0700
Completed: Sat Jul  3 06:34:39 2021 -0700
Published: no
Keep: no

    Packages built:

    * app-vim/gentoo-syntax-20210428-1
    * dev-python/idna-3.2-1
```


The `show` subcommand displays metadata about a given build.

The `diff` subcommand display differences between two build.

```bash
$ gbp diff babette 157 172
diff -r babette/157 babette/172
--- a/babette/157 Wed Jun 16 08:10:04 2021 -0700
+++ b/babette/172 Sat Jul  3 06:31:58 2021 -0700
-app-admin/sudo-1.9.6_p1-r1-1
+app-admin/sudo-1.9.6_p1-r2-1
-app-misc/screen-4.8.0-r2-1
+app-misc/screen-4.8.0-r3-1
-app-vim/gentoo-syntax-20201216-1
+app-vim/gentoo-syntax-20210428-1
-dev-lang/perl-5.32.1-1
+dev-lang/perl-5.32.1-2
+dev-libs/libffi-3.3-r2-1
-dev-python/idna-3.1-2
+dev-python/idna-3.2-1
[...]
```

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish babette 172
```
