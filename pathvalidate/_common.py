# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import dataproperty

from ._error import NullNameError


def _validate_null_string(text, error_msg="null name"):
    if dataproperty.is_empty_string(text):
        raise NullNameError(error_msg)
