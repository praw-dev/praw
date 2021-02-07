#!/usr/bin/env python3
import sys
import tempfile

import docutils.nodes
import docutils.parsers.rst
import docutils.utils


def get_entry_slice(doc):
    current_version = sys.stdin.readline()
    start_line = None
    end_line = None
    for section in doc.children[0].children:
        if start_line:
            end_line = section.children[0].line - 2
            break
        header = section.children[0]
        if current_version in header.rawsource:
            start_line = header.line - 2
    return slice(start_line, end_line)


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(
        components=components
    ).get_default_values()
    settings.report_level = 4
    document = docutils.utils.new_document("<rst-doc>", settings=settings)
    parser.parse(text, document)
    return document


with open("CHANGES.rst") as f:
    source = f.read()
    document = parse_rst(source)

temp_file = f"{tempfile.mkdtemp()}/change_log.txt"

with open(temp_file, "w") as f:
    f.write("\n".join(source.splitlines()[get_entry_slice(document)]))

print(temp_file)
