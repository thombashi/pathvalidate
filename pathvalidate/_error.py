# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals


class NullNameError(ValueError):
    """
    Raised when a name is empty.
    """


class InvalidCharError(ValueError):
    """
    Raised when includes invalid character(s) within a string.
    """


class InvalidCharWindowsError(InvalidCharError):
    """
    Raised when includes Windows specific invalid character(s) within a string.
    """


class InvalidLengthError(ValueError):
    """
    Raised when a string too long/short.
    """


class ReservedNameError(ValueError):
    """
    Raised when a string is matched a reserved name.
    """
