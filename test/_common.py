# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import random
import string


char_list = [x for x in string.digits + string.ascii_letters]


INVALID_PATH_CHARS = [
    "\\", ":", "*", "?", '"', "<", ">", "|",
]
INVALID_FILENAME_CHARS = INVALID_PATH_CHARS + ["/"]

VALID_FILENAME_CHARS = [
    "!", "#", "$", '&', "'", "_",
    "=", "~", "^", "@", "`", "[", "]", "+", "-", ";", "{", "}",
    ",", ".", "(", ")", "%",
]
VALID_PATH_CHARS = VALID_FILENAME_CHARS + ["/"]

INVALID_VAR_CHARS = INVALID_FILENAME_CHARS + [
    "!", "#", "$", '&', "'",
    "=", "~", "^", "@", "`", "[", "]", "+", "-", ";", "{", "}",
    ",", ".", "(", ")", "%",
    " ", "\t", "\n", "\r", "\f", "\v",
]


def make_random_str(length):
    return "".join([random.choice(char_list) for _i in range(length)])