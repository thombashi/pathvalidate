#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import sys

from path import Path
from readmemaker import ReadmeMaker


OUTPUT_DIR = ".."


def write_examples(maker):
    maker.set_indent_level(0)
    maker.write_chapter("Examples")

    example_root = Path("pages").joinpath("examples")

    maker.inc_indent_level()
    maker.write_chapter("Validate a filename")
    maker.write_file(example_root.joinpath("validate_filename_code.txt"))

    maker.write_chapter("Sanitize a filename")
    maker.write_file(example_root.joinpath("sanitize_filename_code.txt"))

    maker.write_chapter("Sanitize a filepath")
    maker.write_file(example_root.joinpath("sanitize_filepath_code.txt"))

    maker.write_chapter("For more information")
    maker.write_lines(
        [
            "More examples are available at ",
            "https://pathvalidate.rtfd.io/en/latest/pages/examples/index.html",
        ]
    )


def main():
    maker = ReadmeMaker(
        "pathvalidate",
        OUTPUT_DIR,
        is_make_toc=True,
        project_url="https://github.com/thombashi/pathvalidate",
    )

    maker.write_introduction_file("badges.txt")

    maker.write_chapter("Summary")
    maker.write_introduction_file("summary.txt")
    maker.write_introduction_file("feature.txt")

    write_examples(maker)

    maker.write_file(maker.doc_page_root_dir_path.joinpath("installation.rst"))

    maker.set_indent_level(0)
    maker.write_chapter("Documentation")
    maker.write_lines(["https://pathvalidate.rtfd.io/"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
