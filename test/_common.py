# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import random
import string
from itertools import product


alphanum_chars = tuple(x for x in string.digits + string.ascii_letters)


INVALID_PATH_CHARS = ("\0",)
INVALID_FILENAME_CHARS = ("/",)
INVALID_WIN_PATH_CHARS = (":", "*", "?", '"', "<", ">", "|") + INVALID_PATH_CHARS
INVALID_WIN_FILENAME_CHARS = INVALID_WIN_PATH_CHARS + INVALID_FILENAME_CHARS + ("\\",)

VALID_FILENAME_CHARS = (
    "!",
    "#",
    "$",
    "&",
    "'",
    "_",
    "=",
    "~",
    "^",
    "@",
    "`",
    "[",
    "]",
    "+",
    "-",
    ";",
    "{",
    "}",
    ",",
    ".",
    "(",
    ")",
    "%",
)
VALID_PATH_CHARS = VALID_FILENAME_CHARS + ("/",)
VALID_PLATFORM_NAMES = ["universal", "linux", "windows", "macos"]

INVALID_JS_VAR_CHARS = INVALID_WIN_FILENAME_CHARS + (
    "!",
    "#",
    "&",
    "'",
    "=",
    "~",
    "^",
    "@",
    "`",
    "[",
    "]",
    "+",
    "-",
    ";",
    "{",
    "}",
    ",",
    ".",
    "(",
    ")",
    "%",
    " ",
    "\t",
    "\n",
    "\r",
    "\f",
    "\v",
)
INVALID_PYTHON_VAR_CHARS = INVALID_JS_VAR_CHARS + ("$",)

WIN_RESERVED_FILE_NAMES = [
    ".",
    "..",
    "CON",
    "con",
    "PRN",
    "prn",
    "AUX",
    "aux",
    "CLOCK$",
    "clock$",
    "NUL",
    "nul",
] + [
    "{:s}{:d}".format(name, num)
    for name, num in product(["COM", "com", "LPT", "lpt"], range(1, 10))
]


def randstr(length, char_list=alphanum_chars):
    return "".join([random.choice(char_list) for _i in range(length)])
