# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import re

from ._common import _preprocess, ascii_symbol_list, unprintable_ascii_char_list
from .error import InvalidCharError


__RE_UNPRINTABLE = re.compile(
    "[{}]".format(re.escape("".join(unprintable_ascii_char_list))), re.UNICODE
)
__RE_SYMBOL = re.compile(
    "[{}]".format(re.escape("".join(ascii_symbol_list + unprintable_ascii_char_list))), re.UNICODE
)


def validate_unprintable(text):
    match_list = __RE_UNPRINTABLE.findall(_preprocess(text))
    if match_list:
        raise InvalidCharError("unprintable character found: {}".format(match_list))


def replace_unprintable(text, replacement_text=""):
    try:
        return __RE_UNPRINTABLE.sub(replacement_text, _preprocess(text))
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")


def validate_symbol(text):
    """
    Verifying whether symbol(s) included in the ``text`` or not.

    :param str text: Input text.
    :raises pathvalidate.InvalidCharError:
        If symbol(s) included in the ``text``.
    """

    match_list = __RE_SYMBOL.findall(_preprocess(text))
    if match_list:
        raise InvalidCharError("invalid symbols found: {}".format(match_list))


def replace_symbol(text, replacement_text="", is_replace_consecutive_chars=False, is_strip=False):
    """
    Replace all of the symbols in the ``text``.

    :param str text: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str

    :Examples:

        :ref:`example-sanitize-symbol`
    """

    try:
        new_text = __RE_SYMBOL.sub(replacement_text, _preprocess(text))
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")

    if not replacement_text:
        return new_text

    if is_replace_consecutive_chars:
        new_text = re.sub("{}+".format(re.escape(replacement_text)), replacement_text, new_text)

    if is_strip:
        new_text = new_text.strip(replacement_text)

    return new_text
