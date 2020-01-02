"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import re
import string
from pathlib import Path

from .error import NullNameError


def is_pathlike_obj(value):
    return isinstance(value, Path)


def validate_null_string(text, error_msg=None):
    if _is_not_null_string(text) or is_pathlike_obj(text):
        return

    if is_null_string(text):
        if not error_msg:
            error_msg = "null name"

        raise NullNameError(error_msg)

    raise TypeError("text must be a string: actual={}".format(type(text)))


def preprocess(name):
    if is_pathlike_obj(name):
        name = str(name)

    return name


def is_null_string(value):
    if value is None:
        return True

    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def _is_not_null_string(value):
    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


def _get_unprintable_ascii_char_list():
    return [chr(c) for c in range(128) if chr(c) not in string.printable]


def _get_ascii_symbol_list():
    symbol_list = []

    for c in range(128):
        c = chr(c)

        if c in unprintable_ascii_chars or c in string.digits + string.ascii_letters:
            continue

        symbol_list.append(c)

    return symbol_list


unprintable_ascii_chars = tuple(_get_unprintable_ascii_char_list())
ascii_symbols = tuple(_get_ascii_symbol_list())

__RE_UNPRINTABLE_CHARS = re.compile(
    "[{}]".format(re.escape("".join(unprintable_ascii_chars))), re.UNICODE
)


def replace_unprintable_char(text, replacement_text=""):
    try:
        return __RE_UNPRINTABLE_CHARS.sub(replacement_text, text)
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")
