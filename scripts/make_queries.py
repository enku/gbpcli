#!/usr/bin/env python
"""Generate the queries.py module from the queries/*.graphql files"""
import sys
from pathlib import Path


def build(src: str, dst: str):
    entries = [*(Path(src) / "src" / "gbpcli" / "queries").glob("*.graphql")]
    entries.sort(key=lambda entry: entry.name)

    dst_path = Path(dst) / "gbpcli" / "queries.py"
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with dst_path.open("w", encoding="UTF-8") as outfile:
        print('"""GraphQL query definitions"""', file=outfile)
        print("# Auto-generated: DO NOT EDIT", file=outfile)
        print("# pylint: disable=line-too-long,invalid-name", file=outfile)

        for entry in entries:
            query = entry.read_text(encoding="UTF-8")

            name = entry.name[:-8]
            print(f"{name} = {query!r}", file=outfile)


def main():
    """Entry point"""
    src = Path(__file__).resolve().parent.parent
    dst = src / "src"
    build(str(src), str(dst))


if __name__ == "__main__":
    main()
