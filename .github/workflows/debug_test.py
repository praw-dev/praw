"""Obtains debug information on the running system."""

import os
import sys

from pip._internal.cli.main import main as pip_invoker

print("Printing python version", sys.version, sep="\n")
print("")
for program in ("pytest",):
    print("Printing information on program {}".format(program))
    pip_invoker(["show", program])
    print("")
print("List of python files in directory:")
for directory, folders, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            print("{}/{}".format(directory.rstrip("/"), file))
