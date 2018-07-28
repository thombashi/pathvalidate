# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import re
import string
import sys

from ._six import text_type
from .error import NullNameError


if sys.version_info[0] == 3:
    unichr = chr
else:
    unichr = unichr


def is_pathlike_obj(value):
    try:
        from pathlib import Path

        return isinstance(value, Path)
    except ImportError:
        return False


def _validate_null_string(text, error_msg="null name"):
    if is_not_null_string(text) or is_pathlike_obj(text):
        return

    if is_null_string(text):
        raise NullNameError(error_msg)

    raise TypeError("text must be a string: actual={}".format(type(text)))


def _preprocess(name):
    if is_pathlike_obj(name):
        return text_type(name)

    return name.strip()


def is_null_string(value):
    if value is None:
        return True

    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def is_not_null_string(value):
    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


def get_unprintable_ascii_char_list():

    return [unichr(c) for c in range(128) if chr(c) not in string.printable]


def get_ascii_symbol_list():
    symbol_list = []

    for c in range(128):
        c = unichr(c)

        if c in unprintable_ascii_char_list or c in string.digits + string.ascii_letters:
            continue

        symbol_list.append(c)

    return symbol_list


unprintable_ascii_char_list = get_unprintable_ascii_char_list()
ascii_symbol_list = get_ascii_symbol_list()

__RE_UNPRINTABLE_CHARS = re.compile(
    "[{}]".format(re.escape("".join(unprintable_ascii_char_list))), re.UNICODE
)


def replace_unprintable_char(text, replacement_text=""):
    try:
        return __RE_UNPRINTABLE_CHARS.sub(replacement_text, text)
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")
