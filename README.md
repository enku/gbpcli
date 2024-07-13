# CLI for Gentoo Build Publisher

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
usage: Command-line interface to Gentoo Build Publisher

Commands:

  * build - Schedule a build for the given machine in CI/CD
  * diff - Handler for subcommand
  * inspect - Show the machines builds as a tree
  * keep - Keep (or release) a build
  * latest - Show the latest build number for a machine
  * list - List a machine's builds
  * logs - Show build logs
  * machines - List machines with builds
  * notes - Show, search, and edit build notes
  * packages - List a build's packages
  * publish - Publish a build
  * pull - Pull a build
  * status - Show build details
  * tag - Add tags builds

positional arguments:
  {build,diff,inspect,keep,latest,list,logs,machines,notes,packages,publish,pull,status,tag}

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --url URL             GBP url
  --color WHEN          colorize output ('always', 'never', 'auto')
  --my-machines MY_MACHINES
                        whitespace-delimited list of machine names to filter
                        on when using the --mine argument. Typically one would
                        instead use the GBPCLI_MYMACHINES environment
                        variable.
```

The URL for the Gentoo Build Publisher may be provided via the command line or
by using the `BUILD_PUBLISHER_URL` environment variable.

To list the machines which have builds use `gbp machines`:

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_machines.svg](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_machines.svg)

The "Latest" column shows the latest build ID for the given machine. If the ID
is in bold it that denotes that the latest build is published (available for
emerges).

To list the available builds for a given machine us `gbp list <machine>`:

![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_list.svg](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_list.svg)

In the above example, the `P` output for build `103` signifies that this build
is currently published.  The `*` flag means that the respective build has new
binary packages. The `K` for build `46` means that the build is marked for
keeping and will not be removed during the purge process. Build `2` has also
been given a "first" tag.  The `N` flag for build `126` means that the build
has a note attached.

```bash
$ gbp status jenkins-buildah 126
```
![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_status.svg](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_status.svg)

Edit/delete build notes using the `gbp notes` command.


The `status` subcommand displays metadata about a given build.  If the build
number is not given, it defaults to the latest build for that machine.

The `diff` subcommand display differences between two builds.

```bash
$ gbp diff jenkins-buildah 103 126
```
![https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_diff.svg](https://raw.githubusercontent.com/enku/gbpcli/master/assets/gbp_diff.svg)

If the second build number is not given, it defaults to the latest build for
that machine.  If the first build number is not given, it defaults to the
published build for that machine.

The `publish` subcommand makes the given build available for syncing and
updating/downgrading.

```bash
$ gbp publish arm64-base 151
```


If the build number is not given, it defaults to the latest build for that
machine.

The `build` subcommand can schedule a build in CI/CD for the given machine,
e.g.:

```bash
$ gbp build babette
```

## Configuration

In addition to the command-line flags, gbpcli can also be configured using a
configuration file. If a the file `~/.config/gbpcli.toml` exists it will be
read and used to configure gbpcli.  This file should be
[toml](https://toml.io/en/) formatted. For example:

```toml
[gbpcli]
url = "http://gbpbox/"
my_machines = ["babette", "lighthouse", "polaris"]
auth = { user = "marduk", api_key = "myapikey" }
```

The `url` setting can be used in place of the `--url` command-line option or
the `BUILD_PUBLISHER_URL` environment variable.  The `my_machines` settings
can be used in place of the `--my-machines` command-line option or the
`GBPCLI_MYMACHINES` environment variable.  The `auth` setting can only be
supplied through the configuration file.
