"""Checks for attributes and code examples in RedditBase subclasses"""

import os
import re
import sys

from praw.models.reddit.base import RedditBase  # noqa: E402
from praw.models.reddit.modmail import ModmailObject  # noqa: E402
from praw.util.cache import cachedproperty  # noqa: E402

# This line imports from the local PRAW rather than the global installed PRAW.
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))


class DocumentationChecker:
    """Checks for code block statements and attribute tables in subclasses.

    Attribute exceptions holds all exceptions. All classes and subclasses in
    the exceptions list will be ignored.

    Attribute METHOD_EXCEPTIONS holds the names of methods that will be
    filtered out.
    """

    BASE_SEARCH_CLASS = RedditBase
    exceptions = {
        ModmailObject,  # is never publicly accessed
    }
    HAS_CODE_BLOCK = re.compile(r".. code-block::")
    HAS_ATTRIBUTE_TABLE = re.compile(r"Attribute[ ]+Description")
    METHOD_EXCEPTIONS = {
        "from_data",
        "id_from_url",
        "parse",
        "sluggify",
    }
    subclasses = set()

    @staticmethod
    def discover_subclasses(base_set):
        working_items = list(base_set)
        subclasses = set()
        while working_items:
            item = working_items.pop(0)
            subclasses.add(item)
            working_items.extend(item.__subclasses__())
        return subclasses

    @classmethod
    def check(cls):
        cls.subclasses |= cls.discover_subclasses(
            cls.BASE_SEARCH_CLASS.__subclasses__()
        )
        cls.exceptions |= cls.discover_subclasses(cls.exceptions)
        success = True
        for subclass in cls.subclasses:
            if subclass in cls.exceptions:
                continue
            if not cls.HAS_ATTRIBUTE_TABLE.search(subclass.__doc__):
                print(
                    "Subclass {mod}.{name} is missing a table "
                    "of common attributes.".format(
                        mod=subclass.__module__, name=subclass.__name__
                    )
                )
                success = False
            for method_name in dir(subclass):
                if method_name in cls.METHOD_EXCEPTIONS:
                    continue
                method = getattr(subclass, method_name)
                if (
                    callable(method) or isinstance(method, cachedproperty)
                ) and not method_name.startswith("_"):
                    if isinstance(method, cachedproperty):
                        method = method.func
                    if not cls.HAS_CODE_BLOCK.search(method.__doc__):
                        print(
                            "Method {mod}.{classname}.{methodname} is missing "
                            "code examples.".format(
                                mod=subclass.__module__,
                                classname=subclass.__name__,
                                methodname=method.__name__,
                            )
                        )
                        success = False
        return success


def main():
    return int(not DocumentationChecker.check())


if __name__ == "__main__":
    sys.exit(main())
