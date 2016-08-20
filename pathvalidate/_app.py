# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

from ._common import _validate_null_string


__INVALID_EXCEL_CHARS = "[]:*?/\\"

__RE_INVALID_EXCEL_SHEET_NAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_EXCEL_CHARS)))


def validate_excel_sheet_name(sheet_name):
    """
    :param str sheet_name: Excel sheet name to validate.
    :raises ValueError:
        If the ``sheet_name`` is empty or includes invalid char(s):
        |invalid_excel_sheet_chars|.
    """

    _validate_null_string(sheet_name)

    match = __RE_INVALID_EXCEL_SHEET_NAME.search(sheet_name)
    if match is not None:
        raise ValueError(
            "invalid char found in the sheet name: '{:s}'".format(
                re.escape(match.group())))


def sanitize_excel_sheet_name(sheet_name, replacement_text=""):
    """
    Replace invalid characters for a Excel sheet name within the ``sheet_name``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_excel_sheet_chars|.

    :param str sheet_name: Excel sheet name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``sheet_name`` is a invalid sheet name.
    """

    try:
        return __RE_INVALID_EXCEL_SHEET_NAME.sub(
            replacement_text, sheet_name.strip())
    except AttributeError as e:
        raise ValueError(e)
