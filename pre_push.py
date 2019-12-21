#!/usr/bin/env python3
"""Run static analysis on the project."""

from os import path

import sys
from shutil import rmtree
from subprocess import CalledProcessError, check_call
from tempfile import mkdtemp


def do_process(args, shell=False):
    """Run program provided by args.

    Return True on success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.
    """
    print("Running: {}".format(" ".join(args)))
    try:
        check_call(args, shell=shell)
    except CalledProcessError:
        print("\nFailed: {}".format(" ".join(args)))
        return False
    except Exception as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(1)
    else:
        return True


def main():
    """Entry point to pre_push.py.
    Returns a statuscode of 0 if everything ran correctly.
    Otherwise, it will return statuscode 1"""
    success = True
    success &= do_process(["black *.py docs praw tests"], shell=True)
    success &= do_process(["flake8", "--exclude=.eggs,build,dist,docs,.tox"])
    success &= do_process(["pydocstyle", "praw"])
    # success &= do_process(["pylint", "--rcfile=.pylintrc", "praw"])

    tmp_dir = mkdtemp()
    try:
        success &= do_process(["sphinx-build", "-W", "docs", tmp_dir])
    finally:
        rmtree(tmp_dir)

    curdir = path.abspath(path.join(__file__, ".."))
    success &= do_process([sys.executable, curdir + "/setup.py", "test"])

    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "pre_push.py: Fail")
    sys.exit(exit_code)

