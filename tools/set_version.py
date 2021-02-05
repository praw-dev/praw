#!/usr/bin/env python3
import re
import sys
from datetime import date

import packaging.version

CHANGELOG_HEADER = "Change Log\n==========\n\n"
UNRELEASED_HEADER = "Unreleased\n----------\n\n"


def add_unreleased_to_changelog():
    with open("CHANGES.rst") as fp:
        content = fp.read()

    if not content.startswith(CHANGELOG_HEADER):
        sys.stderr.write("Unexpected CHANGES.rst header\n")
        return False
    new_header = f"{CHANGELOG_HEADER}{UNRELEASED_HEADER}"
    if content.startswith(new_header):
        sys.stderr.write("CHANGES.rst already contains Unreleased header\n")
        return False

    with open("CHANGES.rst", "w") as fp:
        fp.write(f"{new_header}{content[len(CHANGELOG_HEADER):]}")
    return True


def handle_unreleased():
    return add_unreleased_to_changelog() and increment_development_version()


def handle_version(version):
    version = valid_version(version)
    if not version:
        return False
    return update_changelog(version) and update_package(version)


def increment_development_version():
    with open("praw/const.py") as fp:
        version = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

    parsed_version = valid_version(version)
    if not parsed_version:
        return False

    if parsed_version.is_devrelease:
        pre = "".join(str(x) for x in parsed_version.pre) if parsed_version.pre else ""
        new_version = f"{parsed_version.base_version}{pre}.dev{parsed_version.dev + 1}"
    elif parsed_version.is_prerelease:
        new_version = f"{parsed_version}.dev0"
    else:
        assert parsed_version.base_version == version
        new_version = f"{parsed_version.major}.{parsed_version.minor}.{parsed_version.micro + 1}.dev0"

    assert valid_version(new_version)
    return update_package(new_version)


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} VERSION\n")
        return 1
    if sys.argv[1] == "Unreleased":
        return not handle_unreleased()
    return not handle_version(sys.argv[1])


def update_changelog(version):
    with open("CHANGES.rst") as fp:
        content = fp.read()

    expected_header = f"{CHANGELOG_HEADER}{UNRELEASED_HEADER}"
    if not content.startswith(expected_header):
        sys.stderr.write("CHANGES.rst does not contain Unreleased header.\n")
        return False

    date_string = date.today().strftime("%Y/%m/%d")
    version_line = f"{version} ({date_string})\n"
    version_header = f"{version_line}{'-' * len(version_line[:-1])}\n\n"

    with open("CHANGES.rst", "w") as fp:
        fp.write(f"{CHANGELOG_HEADER}{version_header}{content[len(expected_header):]}")
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

    print(version)
    return True


def valid_version(version):
    parsed_version = packaging.version.parse(version)
    if isinstance(parsed_version, packaging.version.LegacyVersion):
        sys.stderr.write(f"Invalid PEP 440 version: {version}\n")
        return False
    if parsed_version.local or parsed_version.is_postrelease or parsed_version.epoch:
        sys.stderr.write("epoch, local postrelease version parts are not supported")
        return False
    return parsed_version


if __name__ == "__main__":
    sys.exit(main())
