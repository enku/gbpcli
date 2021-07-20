"""Show details for a given build"""
import argparse
import sys
import textwrap

import yarl

from gbpcli import NotFound, utils


def handler(args) -> int:
    """Handler for subcommand"""
    if args.number == 0:
        url = yarl.URL(args.url) / f"api/builds/{args.machine}/latest"
        response = utils.check(args.session.get(str(url)))

        number = response["number"]
    else:
        number = args.number

    url = yarl.URL(args.url) / f"api/builds/{args.machine}/{number}"

    try:
        response = utils.check(args.session.get(str(url)))
    except NotFound:
        print("Build not found", file=sys.stderr)
        return 1

    print(f"Build: {response['name']}/{response['number']}")
    submitted = utils.timestr(response["db"]["submitted"])
    print(f"Submitted: {submitted}")

    completed = utils.timestr(response["db"]["completed"])
    print(f"Completed: {completed}")

    print(f"Published: {utils.yesno(response['storage']['published'])}")
    print(f"Keep: {utils.yesno(response['db']['keep'])}")

    if note := response["db"]["note"]:
        print("")
        lines = note.split("\n")

        for line in lines:
            if len(line) > 70:
                for splitline in textwrap.wrap(response["db"]["note"]):
                    print(f"    {splitline}")
            else:
                print(f"    {line}")
    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("number", type=int, help="build number", nargs="?", default=0)
