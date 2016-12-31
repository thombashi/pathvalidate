# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

import dataproperty as dp
from mbstrdecoder import MultiByteStrDecoder

from ._error import InvalidCharError


__RE_SYMBOL = re.compile(
    "[\0\"\s" + re.escape("\\/:*?<>|!#$&\'=~^@`[]+-;{},.()%_") + "]",
    re.UNICODE)


def validate_symbol(text):
    """
    Verifying whether symbol(s) included in the ``text`` or not.

    :param str text: Input text.
    :raises pathvalidate.InvalidCharError:
        If symbol(s) included in the ``text``.
    """

    match_list = __RE_SYMBOL.findall(
        MultiByteStrDecoder(text).unicode_str)
    if dp.is_not_empty_sequence(match_list):
        raise InvalidCharError("invalid symbols found: {}".format(match_list))


def replace_symbol(text, replacement_text=""):
    """
    Replace all of the symbols in the ``text``.

    :param str text: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str

    :Examples:

        :ref:`example-sanitize-symbol`
    """

    if not dp.StringType(text).is_strict_type():
        raise TypeError("text must be a string")

    return __RE_SYMBOL.sub(
        replacement_text, MultiByteStrDecoder(text).unicode_str)
