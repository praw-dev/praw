#!/usr/bin/env python3
import os
import re
import sys
import time

import packaging.version
import requests

PROJECT = "praw"
HEADERS = {"Authorization": f"token {os.environ.get('READTHEDOCS_TOKEN')}"}


def fetch_versions():
    response = requests.get(
        f"https://readthedocs.org/api/v3/projects/{PROJECT}/versions?active=true",
        headers=HEADERS,
    )
    versions = None
    if response.status_code == 200:
        active_versions = response.json()
        versions = [
            packaging.version.parse(slug["slug"].strip("v"))
            for slug in active_versions["results"]
            if not slug["hidden"] and slug["slug"] not in ["stable", "latest"]
        ]
    if versions is None:
        sys.stderr.write("Failed to get current active versions\n")
    return versions


def main():
    with open(f"{PROJECT}/const.py") as fp:
        current_version = packaging.version.parse(
            re.search('__version__ = "([^"]+)"', fp.read()).group(1)
        )
    if current_version.is_devrelease:
        current_version = packaging.version.parse(
            f"{current_version.major}.{current_version.minor}.{current_version.micro - 1}"
        )
    versions = fetch_versions()
    if versions is None:
        return 1
    max_retry_count = 5
    retry_count = 0
    while current_version not in versions:
        versions = fetch_versions()
        if versions is None:
            return 1
        if current_version in versions:
            break
        else:
            if retry_count >= max_retry_count:
                sys.stderr.write(
                    f"Current version {current_version!s} failed to build\n"
                )
                return 1
            sys.stdout.write("Waiting 30 seconds for build to finish\n")
            retry_count += 1
            time.sleep(30)
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
                sys.stderr.write(f"Failed to hide version {version!s}\n")
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
