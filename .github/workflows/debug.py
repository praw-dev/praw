"""Obtains debug information on the running system."""

import os
import sys

from pip._internal.cli.main import main as pip_invoker

program_list = {
    "lint": ("black", "flake8", "pydocstyle", "sphinx"),
    "test": ("pytest",),
    "test-coverage": ("pytest", "coverage"),
}

debug_mode = sys.argv[1]


def print_group(*print_args, **print_kwargs):
    print(*print_args, **print_kwargs)
    print("-" * 25)


print_group("Running debug script in {} mode".format(debug_mode))

print_group("Printing python version", sys.version, sep="\n")
for program in program_list[debug_mode]:
    print("Printing information on program {}".format(program))
    pip_invoker(["show", program])
    print("*" * 25)

print("List of python files in directory:")
for directory, folders, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            print("{}/{}".format(directory.rstrip("/"), file))
