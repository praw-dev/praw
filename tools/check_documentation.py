"""Checks for attributes and code examples in RedditBase subclasses"""

import os
import re
import sys
import traceback

from typing import Any, Callable, List, Set, Type, Union

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
    def discover_subclasses(base: Union[List[Type], Set[Type]]) -> Set[Type]:
        """Discover the subclasses of a base set of classes, recursively.

        :param base: A list or set containing types.
        :returns: A set of types.
        """
        working_items = list(base)
        subclasses = set()
        while working_items:
            item = working_items.pop(0)
            subclasses.add(item)
            working_items.extend(item.__subclasses__())
        return subclasses

    @staticmethod
    def determine_second_non_empty_line(line_list: List[str]) -> str:
        """Determine the second line of a list of line that isn't whitespace.

        :param line_list: A list of lines
        :returns: The second non-empty line
        """
        return next(line for line in line_list[1:] if line.strip())

    @staticmethod
    def determine_next_whitespace_line(line_list: List[str]) -> int:
        """Determine the index of the first line of whitespace only.

        :param line_list: A list of lines
        :return: The index of the whitespace line
        """
        return next(
            num for num, line in enumerate(line_list) if not line.strip()
        )

    @staticmethod
    def determine_whitespace(string: str) -> int:
        """Determine the amount of spaces before the first non-space character.

        :param string: The string to check.
        :returns: The number of spaces.
        """
        count = 0
        while string[0] == " ":
            count += 1
            string = string[1:]
        return count

    @classmethod
    def determine_attribute_table(cls, check_class: Type) -> bool:
        """Determine if a class's documentation contains an attribute table.

        If a table is not found, a message is printed to stdout.

        :param check_class: The class to check.
        :returns: A boolean indicating if the class had an attribute table.
        """
        status = bool(cls.HAS_ATTRIBUTE_TABLE.search(check_class.__doc__))
        if not status:
            print(
                "Subclass {mod}.{name} is missing a table "
                "of common attributes.".format(
                    mod=check_class.__module__, name=check_class.__name__
                )
            )
        return status

    @classmethod
    def determine_code_block(
        cls, callable: Callable[[Any], Any], parent_class: Type
    ) -> bool:
        """Determine if the callable has code-block directives.

        :param callable: Any callable.
        :param parent_class: The class the method belongs to.
        :returns: The status of the check.
        """
        status = bool(cls.HAS_CODE_BLOCK.search(callable.__doc__))
        if not status:
            print(
                "Method {mod}.{classname}.{methodname} is missing code "
                "examples.".format(
                    mod=parent_class.__module__,
                    classname=parent_class.__name__,
                    methodname=callable.__name__,
                )
            )
        return status

    @classmethod
    def determine_code_block_formatting(
        cls, callable: Callable[[Any], Any], parent_class: Type
    ) -> bool:
        """Determine if the code blocks in a callable are accurately formatted.

        :param callable: Any callable.
        :param parent_class: The class the method belongs to.
        :returns: The status of the check.
        """
        status = True
        lines = callable.__doc__.splitlines(False)
        whitespace = (
            cls.determine_whitespace(
                cls.determine_second_non_empty_line(lines)
            )
            + 4
        )
        blocks = callable.__doc__.split(".. code-block:: ")
        for blocknum, block in enumerate(blocks[1:], start=1):
            block_lines = block.splitlines(False)
            if not bool(block_lines[0].strip()):
                print(
                    "Code block #{codeblocknum} in {mod}.{classname}."
                    "{methodname} missing a language type".format(
                        mod=parent_class.__module__,
                        classname=parent_class.__name__,
                        methodname=callable.__name__,
                        codeblocknum=blocknum,
                    )
                )
                status = False
            if bool(block_lines[1].strip()):
                print(
                    "Code block #{codeblocknum} in {mod}.{classname}."
                    "{methodname} missing a seperator.".format(
                        mod=parent_class.__module__,
                        classname=parent_class.__name__,
                        methodname=callable.__name__,
                        codeblocknum=blocknum,
                    )
                )
                status = False
            stop = 2 + cls.determine_next_whitespace_line(block_lines[2:])
            actual_lines = []
            for lineno, line in enumerate(block_lines[2:stop], start=2):
                if bool(line[0:whitespace].strip()):
                    print(
                        "Line {codeblocklinenum} of Code block #{codeblocknum}"
                        " in {mod}.{classname}.{methodname} not correctly "
                        "indented.".format(
                            mod=parent_class.__module__,
                            classname=parent_class.__name__,
                            methodname=callable.__name__,
                            codeblocknum=blocknum,
                            codeblocklinenum=lineno,
                        )
                    )
                    status = False
                else:
                    actual_lines.append(line[whitespace:])
            if block_lines[0].strip().lower() == "python":
                exec_str = "\n".join(actual_lines)
                try:
                    exec(exec_str)
                except SyntaxError:
                    print(
                        "Code block #{codeblocknum} in {mod}.{classname}."
                        "{methodname} contains syntax errors.".format(
                            mod=parent_class.__module__,
                            classname=parent_class.__name__,
                            methodname=callable.__name__,
                            codeblocknum=blocknum,
                        )
                    )
                    traceback.print_exc(file=sys.stdout)
                    status = False
                except Exception:
                    pass
        return status

    @classmethod
    def check(cls) -> bool:
        cls.subclasses |= cls.discover_subclasses(
            cls.BASE_SEARCH_CLASS.__subclasses__()
        )
        cls.exceptions |= cls.discover_subclasses(cls.exceptions)
        success = True
        for subclass in cls.subclasses:
            if subclass in cls.exceptions:
                continue
            success &= cls.determine_attribute_table(subclass)
            for method_name in dir(subclass):
                if method_name in cls.METHOD_EXCEPTIONS:
                    continue
                method = getattr(subclass, method_name)
                if (
                    callable(method) or isinstance(method, cachedproperty)
                ) and not method_name.startswith("_"):
                    if isinstance(method, cachedproperty):
                        method = method.func
                    method_status = cls.determine_code_block(method, subclass)
                    success &= method_status
                    if method_status:
                        success &= cls.determine_code_block_formatting(
                            method, subclass
                        )
        return success


def main() -> int:
    return int(not DocumentationChecker.check())


if __name__ == "__main__":
    sys.exit(main())
