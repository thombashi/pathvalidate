#!/usr/bin/env python
# encoding: utf-8

import sys

import readmemaker


OUTPUT_DIR = ".."


def write_examples(maker):
    maker.set_indent_level(0)
    maker.write_chapter("Examples")

    maker.inc_indent_level()
    maker.write_chapter("Validate a filename")
    maker.write_example_file("validate_filename_code.txt")

    maker.write_chapter("Sanitize a filename")
    maker.write_example_file("sanitize_filename_code.txt")

    maker.write_chapter("Sanitize a variable name")
    maker.write_example_file("sanitize_var_name_code.txt")

    maker.write_chapter("For more information")
    maker.write_line_list([
        "More examples are available at ",
        "http://pathvalidate.readthedocs.org/en/latest/pages/examples/index.html",
    ])


def main():
    maker = readmemaker.ReadmeMaker("pathvalidate", OUTPUT_DIR)

    maker.write_introduction_file("badges.txt")

    maker.inc_indent_level()
    maker.write_chapter("Summary")
    maker.write_introduction_file("summary.txt")

    write_examples(maker)

    maker.write_file(
        maker.doc_page_root_dir_path.joinpath("installation.rst"))

    maker.set_indent_level(0)
    maker.write_chapter("Documentation")
    maker.write_line_list([
        "http://pathvalidate.readthedocs.org/en/latest/"
    ])


if __name__ == '__main__':
    sys.exit(main())
