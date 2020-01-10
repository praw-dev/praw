import argparse
import os
import sys


class StaticCheck:
    """Run simple checks on the entire document or specific lines."""

    def __init__(self, replace: bool):
        self.full_file_checks = [
            # add more checks to the list as they are added
        ]
        self.line_checks = [
            self.check_for_noreturn,
            self.check_for_double_r,
            self.check_for_double_u,
            # add more checks to the list as they are added
        ]
        self.replace = replace

    def check_for_noreturn(
        self, filename: str, lineno: str, content: str
    ) -> bool:
        if "noreturn" in content.lower():
            print(
                "{filename}: Line {line_number} has phrase noreturn, "
                "please edit and remove this.".format(
                    filename=filename, line_number=lineno
                )
            )
            return False
        return True

    def check_for_double_r(
        self, filename: str, lineno: str, content: str
    ) -> bool:
        if "/r/" in content:
            # checks for reddit.com urls
            content = content.replace("/r/", "r/")
            content = content.replace(
                "reddit.comr/", "reddit.com/r/"
            )  # handles reddit.com/r/... urls
        if "/r/" in content:
            if self.replace:
                with open(filename, "w", encoding="utf-8") as fp:
                    fp.write(content)
                print(
                    "{filename}: Replaced all ``/r/`` in line # {line_number} "
                    "to ``r/``".format(filename=filename, line_number=lineno)
                )
                return True
            print(
                "{filename}: Line # {line_number} uses the old ``/r/`` syntax"
                ", please change the syntax to ``r/``.".format(
                    filename=filename, line_number=lineno
                )
            )
            return False
        return True

    def check_for_double_u(
        self, filename: str, lineno: str, content: str
    ) -> bool:
        if "/u/" in content:
            # checks for reddit.com urls
            content = content.replace("/u/", "u/")
            content = content.replace(
                "reddit.comu/", "reddit.com/u/"
            )  # handles reddit.com/u/... urls
        if "/u/" in content:
            if self.replace:
                with open(filename, "w", encoding="utf-8") as fp:
                    fp.write(content)
                print(
                    "{filename}: Replaced all ``/u/`` in line # {line_number} "
                    "to ``u/``".format(filename=filename, line_number=lineno)
                )
                return True
            print(
                "{filename}: Line # {line_number} uses the old ``/u/`` syntax"
                ", please change the syntax to ``u/``.".format(
                    filename=filename, line_number=lineno
                )
            )
            return False
        return True

    def run_checks(self) -> bool:
        status = True
        directory = os.path.abspath(os.path.join(__file__, "..", "..", "praw"))
        for current_directory, directories, filenames in os.walk(directory):
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                filename = os.path.join(current_directory, filename)
                with open(filename, encoding="utf-8") as fp:
                    lines = fp.readlines()
                full_content = "".join(lines)
                for check in self.full_file_checks:
                    status |= check(filename, full_content)
                for lineno, line in enumerate(lines, 1):
                    for check in self.line_checks:
                        status |= check(filename, lineno, line)
        return status


def main():
    parser = argparse.ArgumentParser(
        description="Run static line checks and optionally replace values that"
        "should not be used."
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
    check = StaticCheck(args.replace)
    return check.run_checks()


if __name__ == "__main__":
    sys.exit(int(not main()))  # True -> False, False -> 0 (success)
