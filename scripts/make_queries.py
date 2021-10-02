#!/usr/bin/env python
"""Generate the queries.py module from the queries/*.graphql files"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
GRAPHQL_DIR = DIR / "src" / "gbpcli" / "queries"


def main():
    """Entry point"""
    entries = [Path(entry) for entry in sys.argv[1:]]
    entries.sort(key=lambda entry: entry.name)
    print('"""GraphQL query definitions"""')
    print("# Auto-generated: DO NOT EDIT")
    print("# pylint: disable=line-too-long,invalid-name")
    for entry in entries:
        with entry.open(encoding="utf-8") as graphql:
            query = graphql.read()

        name = entry.name[:-8]
        print(f"{name} = {query!r}")


if __name__ == "__main__":
    main()
