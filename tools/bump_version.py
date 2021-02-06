#!/usr/bin/env python3
import sys

COMMIT_PREFIX = "Bump to v"


def main():
    line = sys.stdin.readline()
    if not line.startswith(COMMIT_PREFIX):
        sys.stderr.write(
            f"Commit message does not begin with `{COMMIT_PREFIX}`.\nMessage:\n\n{line}"
        )
        return 1
    print(line[len(COMMIT_PREFIX) : -1])


if __name__ == "__main__":
    sys.exit(main())
