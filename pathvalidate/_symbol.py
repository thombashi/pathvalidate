# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

import dataproperty

from ._error import InvalidCharError


__RE_SYMBOL = re.compile("[^a-zA-Z0-9]")


def validate_symbol(text):
    """
    Raise an exception if symbol(s) included in ``text``.

    :param str text: Input text.
    :raiss InvalidCharError: If the ``text`` includes symbol(s)
    """

    re_symbol = re.compile("[^a-zA-Z0-9]+")
    match_list = re_symbol.findall(text)
    if dataproperty.is_not_empty_sequence(match_list):
        raise InvalidCharError("invalid symbols found: {}".format(match_list))


def replace_symbol(text, replacement_text=""):
    """
    Replace all of the symbols in text.

    :param str text: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    return __RE_SYMBOL.sub(replacement_text, text)
