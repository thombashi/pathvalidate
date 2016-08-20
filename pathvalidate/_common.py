# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import dataproperty


def __validate_null_string(text):
    if dataproperty.is_empty_string(text):
        raise ValueError("null name")
