import ast
import os
import re
from ast import ClassDef, FunctionDef, get_docstring
from os.path import basename

import black
import docutils.nodes
import docutils.parsers.rst
import docutils.utils

mode = black.Mode(
    target_versions={black.TargetVersion.PY36},
    line_length=88,
    string_normalization=False,
    is_pyi=False,
)

DOCSTRING_INCORRECT_FORMAT = re.compile(r"( +)\.\. code-block:: python\n\n\1 {3}[\w#]")

current = None
current_file = None
failed = False
skip_files = ["gildable.py"]


class Visitor(docutils.nodes.NodeVisitor):
    def visit_literal_block(self, node: docutils.nodes.literal_block) -> None:
        """Called for "literal_block" nodes."""
        global current
        global current_file
        global failed
        if node.attributes["classes"] == ["code", "python"]:
            try:
                formatted = black.format_str(node.rawsource, mode=mode)
            except black.InvalidInput as error:
                print(f"Syntax error in {current_file}:{current.lineno}: {error}")
                failed = True
                return
            needsReformatted = formatted != f"{node.rawsource}\n"
            if needsReformatted:
                print(
                    f"{current_file}:{current.lineno} Object: {current.name} at line"
                    f" {current.lineno}:\n{node.rawsource}\n\nNeeds reformatted"
                    f" to:\n\n{formatted}"
                )
                failed = True

    def unknown_visit(self, node) -> None:
        """Called for all other node types."""
        pass


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(
        components=components
    ).get_default_values()
    settings.report_level = 4
    document = docutils.utils.new_document("<rst-doc>", settings=settings)
    if basename(current_file) not in skip_files:
        parser.parse(text, document)
    return document


def get_docstrings(file_ast):
    return [
        (get_docstring(i, False), i)
        for i in [i for i in ast.walk(file_ast)]
        if isinstance(i, (ClassDef, FunctionDef))
    ]


def get_ast(file_path):
    with open(file_path) as f:
        contents = f.read()
        if DOCSTRING_INCORRECT_FORMAT.search(contents):
            print(file_path)
    return ast.parse(contents, filename=os.path.basename(file_path))


def main():
    global current
    global current_file
    for subdir, dirs, files in os.walk("./praw"):
        for file in files:
            file_path = os.path.join(subdir, file)

            if file_path.endswith(".py"):
                file_ast = get_ast(file_path)
                current_file = file_path
                for docstring, item in get_docstrings(file_ast):
                    current = item
                    if docstring:
                        doc = parse_rst(docstring)
                        visitor = Visitor(doc)
                        doc.walk(visitor)


if __name__ == "__main__":
    main()
    exit(int(failed))
