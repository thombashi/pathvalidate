#!/usr/bin/env python
# encoding: utf-8

import os
import re
import sys


VERSION = "0.4.3"
OUTPUT_DIR = ".."
README_WORK_DIR = "."
DOC_PAGE_DIR = os.path.join(README_WORK_DIR, "pages")


def get_usage_file_path(filename):
    return os.path.join(DOC_PAGE_DIR, "examples", filename)


def replace_for_pypi(line):
    line = line.replace(".. code-block::", ".. code::")
    line = line.replace(".. code:: none", ".. code::")

    return line


def write_line_list(f, line_list):
    f.write("\n".join([
        replace_for_pypi(line)
        for line in line_list
        if re.search(":caption:", line) is None
    ]))
    f.write("\n" * 2)


def write_usage_file(f, filename):
    with open(get_usage_file_path(filename)) as f_usage_file:
        write_line_list(
            f, [line.rstrip()for line in f_usage_file.readlines()])


def write_examples(f):
    write_line_list(f, [
        "Examples",
        "========",
    ])

    write_line_list(f, [
        "Filename validation",
        "----------------------------",
    ])
    write_usage_file(f, "validate_code.txt")

    write_line_list(f, [
        "Sanitize a file path",
        "----------------------------",
    ])
    write_usage_file(f, "sanitize_file_path_code.txt")

    write_line_list(f, [
        "For more information",
        "--------------------",
        "More examples are available at ",
        "http://pathvalidate.readthedocs.org/en/latest/pages/examples/index.html",
        "",
    ])


def main():
    with open(os.path.join(OUTPUT_DIR, "README.rst"), "w") as f:
        write_line_list(f, [
            "pathvalidate",
            "=============",
            "",
        ] + [
            line.rstrip() for line in
            open(os.path.join(
                DOC_PAGE_DIR, "introduction", "badges.txt")).readlines()
        ])

        write_line_list(f, [
            "Summary",
            "-------",
            "",
        ] + [
            line.rstrip() for line in
            open(os.path.join(
                DOC_PAGE_DIR, "introduction", "summary.txt")).readlines()
        ])

        write_examples(f)

        write_line_list(f, [
            line.rstrip() for line in
            open(os.path.join(DOC_PAGE_DIR, "installation.rst")).readlines()
        ])

        write_line_list(f, [
            "Documentation",
            "=============",
            "",
            "http://pathvalidate.readthedocs.org/en/latest/"
        ])


if __name__ == '__main__':
    sys.exit(main())
