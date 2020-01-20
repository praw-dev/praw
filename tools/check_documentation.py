"""Checks for attributes and code examples in RedditBase subclasses"""

import os
import re
import sys

# This line imports from the local PRAW rather than the global installed PRAW.
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))

from praw.models.reddit.base import RedditBase  # noqa: E402
from praw.models.reddit.modmail import ModmailObject  # noqa: E402
from praw.util.cache import cachedproperty  # noqa: E402


class DocumentationChecker:
    """Checks for code block statements and attribute tables in subclasses.

    Attribute exceptions holds all exceptions. All classes and subclasses in
    the exceptions list will be ignored.

    Attribute METHOD_EXCEPTIONS holds the names of methods that will be
    filtered out.
    """

    BASE_SEARCH_CLASS = RedditBase
    exceptions = [
        ModmailObject,  # is never publicly accessed
    ]
    HAS_CODE_BLOCK = re.compile(r".. code-block::")
    HAS_ATTRIBUTE_TABLE = re.compile(r"Attribute[ ]+Description")
    METHOD_EXCEPTIONS = [
        "from_data",
        "id_from_url",
        "parse",
        "sluggify",
    ]
    subclasses = []

    @staticmethod
    def in_list_lambda(search_list):
        return lambda item: item not in search_list

    @classmethod
    def expand(cls, base_list, append_list):
        base_list = list(base_list)
        while len(base_list) > 0:
            item = base_list.pop(0)
            append_list.append(item)
            base_list.extend(item.__subclasses__())
        append_list = set(append_list)

    @classmethod
    def check(cls):
        cls.expand(
            cls.BASE_SEARCH_CLASS.__subclasses__(), cls.subclasses
        )
        cls.expand(cls.exceptions, cls.exceptions)
        success = True
        for subclass in (
            item for item in cls.subclasses if item not in cls.exceptions
        ):
            if not cls.HAS_ATTRIBUTE_TABLE.search(subclass.__doc__):
                print(
                    "Subclass {mod}.{name} is missing a table "
                    "of common attributes.".format(
                        mod=subclass.__module__, name=subclass.__name__
                    )
                )
                success = False
            method_list = []
            for method_name in (
                item
                for item in dir(subclass)
                if item not in cls.METHOD_EXCEPTIONS
            ):
                value = getattr(subclass, method_name)
                if (
                    callable(value) or isinstance(value, cachedproperty)
                ) and not method_name.startswith("_"):
                    method_list.append(value)
            for method in method_list:
                if isinstance(method, cachedproperty):
                    method = method.func
                method_doc = method.__doc__
                if not cls.HAS_CODE_BLOCK.search(str(method_doc)):
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
