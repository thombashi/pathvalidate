# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re


__RE_SYMBOL = re.compile("[^a-zA-Z0-9]")


def replace_symbol(text, replacement_text=""):
    """
    Replace all of the symbols.

    :param str text: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    return __RE_SYMBOL.sub(replacement_text, text)
