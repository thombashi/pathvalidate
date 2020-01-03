"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import re
import string
from pathlib import Path
from typing import Any, List, Optional, Union, cast

from .error import NullNameError


PathType = Union[str, Path]


def is_pathlike_obj(value: PathType) -> bool:
    return isinstance(value, Path)


def validate_null_string(text: PathType, error_msg: Optional[str] = None) -> None:
    if _is_not_null_string(text) or is_pathlike_obj(text):
        return

    if is_null_string(text):
        if not error_msg:
            error_msg = "null name"

        raise NullNameError(error_msg)

    raise TypeError("text must be a string: actual={}".format(type(text)))


def preprocess(name: PathType) -> str:
    if is_pathlike_obj(name):
        name = str(name)

    return cast(str, name)


def is_null_string(value: Any) -> bool:
    if value is None:
        return True

    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def _is_not_null_string(value: Any) -> bool:
    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


def _get_unprintable_ascii_char_list() -> List[str]:
    return [chr(c) for c in range(128) if chr(c) not in string.printable]


def _get_ascii_symbol_list() -> List[str]:
    symbol_list = []  # type: List[str]

    for i in range(128):
        c = chr(i)

        if c in unprintable_ascii_chars or c in string.digits + string.ascii_letters:
            continue

        symbol_list.append(c)

    return symbol_list


unprintable_ascii_chars = tuple(_get_unprintable_ascii_char_list())
ascii_symbols = tuple(_get_ascii_symbol_list())

__RE_UNPRINTABLE_CHARS = re.compile(
    "[{}]".format(re.escape("".join(unprintable_ascii_chars))), re.UNICODE
)


def replace_unprintable_char(text: str, replacement_text: str = "") -> str:
    try:
        return __RE_UNPRINTABLE_CHARS.sub(replacement_text, text)
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")
