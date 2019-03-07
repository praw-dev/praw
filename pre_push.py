#!/usr/bin/env python3
"""Run static analysis on the project."""
from shutil import rmtree
from subprocess import CalledProcessError, check_call
from tempfile import mkdtemp
import sys


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
    return True


def main():
    """Entry point to pre_push.py."""
    success = True
    success &= do_process(["black -l 79 *.py docs praw tests"], shell=True)
    success &= do_process(["flake8", "--exclude=.eggs,docs,.tox"])
    success &= do_process(["pydocstyle", "praw"])
    # success &= do_process(["pylint", "--rcfile=.pylintrc", "praw"])

    tmp_dir = mkdtemp()
    try:
        success &= do_process(["sphinx-build", "-W", "docs", tmp_dir])
    finally:
        rmtree(tmp_dir)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    print()
    print("pre_push.py: Success!" if exit_code == 0 else "pre_push.py: Fail")
    sys.exit(exit_code)
