#!/usr/bin/env python3
import os
import re
import sys

import packaging.version
import requests

PROJECT = "praw"
HEADERS = {"Authorization": f"token {os.environ.get('READTHEDOCS_TOKEN')}"}


def main():
    with open("praw/const.py") as fp:
        current_version = packaging.version.parse(
            re.search('__version__ = "([^"]+)"', fp.read()).group(1)
        )

    response = requests.get(
        f"https://readthedocs.org/api/v3/projects/{PROJECT}/versions?active=true",
        headers=HEADERS,
    )

    if response.status_code != 200:
        sys.stderr.write("Failed to get current active versions\n")
        return True
    active_versions = response.json()
    versions = [current_version] + [
        packaging.version.parse(slug["slug"].strip("v"))
        for slug in active_versions["results"]
        if not slug["hidden"] and not slug["slug"] in ["current", "latest"]
    ]
    aggregated_versions = {}
    for version in versions:
        aggregated_versions.setdefault(version.major, [])
        aggregated_versions[version.major].append(version)

    latest_major_versions = [
        max(aggregated_versions[major]) for major in aggregated_versions
    ]
    major_versions = [version.major for version in versions]
    is_new_major = major_versions.count(current_version.major) == 1

    for version in versions:
        if (is_new_major and version not in latest_major_versions) or (
            (version.major, version.minor)
            == (
                current_version.major,
                current_version.minor,
            )
            and version.micro != current_version.micro
        ):
            response = requests.patch(
                f"https://readthedocs.org/api/v3/projects/{PROJECT}/versions/v{version}/",
                json={"active": True, "hidden": True},
                headers=HEADERS,
            )
            if response.status_code == 204:
                sys.stderr.write(f"Version {version!s} was hidden successfully\n")
            else:
                sys.stderr.write(f"Failed to hide version {version}\n")
                return True
    return False


if __name__ == "__main__":
    sys.exit(main())
