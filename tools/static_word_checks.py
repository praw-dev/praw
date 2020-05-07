import argparse
import os
import re
import sys


class StaticChecker:
    """Run simple checks on the entire document or specific lines."""

    def __init__(self, replace: bool):
        """Instantiates the class.

        :param replace: Whether or not to make replacements.
        """
        self.full_file_checks = [
            self.check_for_code_statement,
            self.check_for_double_syntax
            # add more checks to the list as they are added
        ]
        self.line_checks = [
            self.check_for_noreturn,
            # add more checks to the list as they are added
        ]
        self.replace = replace

    def check_for_code_statement(self, filename: str, content: str) -> bool:
        """Checks the code for ``.. code::`` statements.

        :param filename: The name of the file to check & replace.
        :param content: The content of the file
        :returns: A boolean with the status of the check
        """
        if ".. code::" in content:
            newcontent = content.replace(".. code::", ".. code-block::")
            if self.replace:
                with open(filename, "w") as fp:
                    fp.write(newcontent)
                print(
                    "{filename}: Replaced all ``code::`` to "
                    "``code-block::``".format(filename=filename)
                )
                return True
            print(
                "{filename}; This file uses the `code::` syntax, please change"
                " the syntax to ``code-block::``.".format(filename=filename)
            )
            return False
        return True

    def check_for_double_syntax(self, filename: str, content: str) -> bool:
        """Checks a file for double-slash statements (``/r/`` and ``/u/``).

        :param filename: The name of the file to check & replace.
        :param content: The content of the file
        :returns: A boolean with the status of the check
        """
        if (
            os.path.join("praw", "const.py")  # fails due to bytes blocks
            in filename
        ):
            return True
        newcontent = re.sub(r"(^|\s)/(u|r)/", r"\1\2/", content)
        # will only replace if the character behind a /r/ is a
        # whitespace character or the start of a line
        if content == newcontent:
            return True
        if self.replace:
            with open(filename, "w") as fp:
                fp.write(newcontent)
            print(
                "{filename}: Replaced all instances of ``/r/`` and/or "
                "``/u/`` to ``r/`` and/or ``u/``.".format(filename=filename)
            )
            return True
        print(
            "{filename}: This file contains instances of ``/r/`` and/or "
            "``/u/``. Please change them to ``r/`` and/or "
            "``u/``.".format(filename=filename)
        )
        return False

    def check_for_noreturn(
        self, filename: str, line_number: int, content: str
    ) -> bool:
        """Checks a line for ``NoReturn`` statements.

        :param filename: The name of the file to check & replace.
        :param line_number: The line number
        :param content: The content of the line
        :returns: A boolean with the status of the check
        """
        if "noreturn" in content.lower():
            print(
                "{filename}: Line {line_number} has phrase ``noreturn``, "
                "please edit and remove this.".format(
                    filename=filename, line_number=line_number
                )
            )
            return False
        return True

    def run_checks(self) -> bool:
        """Scan a directory and run the checks.

        The directory is assumed to be the praw directory located in the parent
        directory of the file, so if this file exists in
        ``~/praw/tools/static_word_checks.py``, it will check ``~/praw/praw``.

        It runs the checks located in the ``self.full_file_checks`` and
        ``self.line_checks`` lists, with full file checks being run first.

        Full-file checks are checks that can also fix the errors they find,
        while the line checks can just warn about found errors.

        * Full file checks:

            * :meth:`.check_for_code_statement`
            * :meth:`.check_for_double_syntax`

        * Line checks

            * :meth:`.check_for_noreturn`
        """
        status = True
        directory = os.path.abspath(os.path.join(__file__, "..", "..", "praw"))
        for current_directory, directories, filenames in os.walk(directory):
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                filename = os.path.join(current_directory, filename)
                for check in self.full_file_checks:
                    # this is done to make sure that the checks are not
                    # replacing each other and creating an infinite loop
                    with open(filename) as fp:
                        full_content = fp.read()
                    status &= check(filename, full_content)
                for check in self.line_checks:
                    # this is done to make sure that the checks are not
                    # replacing each other and creating an infinite loop
                    with open(filename) as fp:
                        lines = fp.readlines()
                    for line_number, line in enumerate(lines, 1):
                        status &= check(filename, line_number, line)
        return status


def main():
    """The main function."""
    parser = argparse.ArgumentParser(
        description="Run static line checks and optionally replace values that"
        " should not be used."
    )
    parser.add_argument(
        "-r",
        "--replace",
        action="store_true",
        default=False,
        help="If it is possible, tries to reformat values. Not all checks "
        "can reformat values, and those will have to be edited manually.",
    )
    args = parser.parse_args()
    check = StaticChecker(args.replace)
    return int(not check.run_checks())  # True -> False, False -> 0 (success)


if __name__ == "__main__":
    sys.exit(main())
