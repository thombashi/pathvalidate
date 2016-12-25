# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

import dataproperty as dp
from mbstrdecoder import MultiByteStrDecoder

from ._common import _validate_null_string
from ._error import InvalidCharError


__RE_LTSV_LABEL = re.compile("[^0-9A-Za-z_.-]")


def validate_ltsv_label(label):
    """
    Verifying whether ``label`` is a valid
    `Labeled Tab-separated Values (LTSV) <http://ltsv.org/>`__ label or not.

    :param str label: Label to validate.
    :raises pathvalidate.NullNameError: If the ``label`` is empty.
    :raises pathvalidate.InvalidCharError:
        If invalid character(s) found in the ``label`` for a LTSV format label.
    """

    _validate_null_string(label, error_msg="label is empty")

    match_list = __RE_LTSV_LABEL.findall(
        MultiByteStrDecoder(label).unicode_str)
    if dp.is_not_empty_sequence(match_list):
        raise InvalidCharError(
            "invalid character found for a LTSV format label: {}".format(
                match_list))


def sanitize_ltsv_label(label, replacement_text=""):
    """
    Replace all of the symbols in text.

    :param str label: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    _validate_null_string(label, error_msg="label is empty")

    return __RE_LTSV_LABEL.sub(
        replacement_text, MultiByteStrDecoder(label).unicode_str)
