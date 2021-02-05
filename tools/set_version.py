#!/usr/bin/env python3
import re
import sys
from datetime import date


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} VERSION\n")
        return 1

    success = update_changelog(sys.argv[1]) and update_package(sys.argv[1])
    return not success


def update_changelog(version):
    lines = []
    skip_hyphens = False
    version_set = False
    with open("CHANGES.rst") as fp:
        for line in fp:
            if line == "Unreleased\n":
                date_string = date.today().strftime("%Y/%m/%d")
                version_string = f"{version} ({date_string})\n"
                lines.append(version_string)
                lines.append(f"{'-' * len(version_string[:-1])}\n")
                skip_hyphens = True
                version_set = True
            elif skip_hyphens:
                assert line == "----------\n"
                skip_hyphens = False
            else:
                lines.append(line)

    if not version_set:
        sys.stderr.write("No version string set. `Unreleased` not found.\n")
        return False

    with open("CHANGES.rst", "w") as fp:
        fp.write("".join(lines))

    return True


def update_package(version):
    with open("praw/const.py") as fp:
        content = fp.read()

    updated = re.sub('__version__ = "([^"]+)"', f'__version__ = "{version}"', content)
    if content == updated:
        sys.stderr.write("Package version string not changed\n")
        return False

    with open("praw/const.py", "w") as fp:
        fp.write(updated)

    return True


if __name__ == "__main__":
    sys.exit(main())
