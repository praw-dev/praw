#!/usr/bin/env python3

import argparse
import os
import sys
from typing import AnyStr


def check_for_double_backslash(filename: AnyStr, check: bool):
    """Check a file and replace ``/u/`` and ``/r/` to ``u/`` and ``r/``.

    :param filename: The file to open
    :param check: Whether or not the program is operating in ``check`` mode.
        In check mode, the program will exit with a status 1 if files will be
        replaced. In non-check mode, the program will replace files.
    """
    status = 0
    with open(filename, "r", encoding="utf-8") as fp:
        old_content = fp.read()
    new_content = old_content.replace("/u/", "u/").replace("/r/", "r/")
    new_content = old_content.replace(
        "reddit.comr/", "reddit.com/r/"
    )  # handles reddit.com/r/... urls
    if old_content == new_content:
        return 0
    if check:
        status = 1
        print(
            "File {filename} contains ``/u/`` or ``/r/`` statements!".format(
                filename=filename
            )
        )
    else:
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(new_content)
        print(
            "Replaced ``/u/`` and ``/r/`` statements to ``u/`` and ``r/`` in "
            "{filename}".format(filename=filename)
        )
    return status


def main():
    parser = argparse.ArgumentParser(
        description="Check and reformat praw's usage of ``/u/`` and ``/r/` to "
        "``u/`` and ``r/``."
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        default=False,
        help="Check files but do not reformat. Exits if a filename"
        " can be reformatted.",
    )
    parsed = parser.parse_args()
    check = parsed.check
    status = 0
    for current_directory, directories, filenames in os.walk(
        os.path.abspath(os.path.join(__file__, "..", "..", "praw"))
    ):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            if filename.endswith("endpoints.py"):
                # we do not want to mess with reddit endpoints
                continue
            filename = os.path.join(current_directory, filename)
            status |= check_for_double_backslash(filename, check)
    return status


if __name__ == "__main__":
    sys.exit(main())
