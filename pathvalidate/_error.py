# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals


class InvalidNameError(ValueError):
    """
    Base class of invalid name error.
    """


class NullNameError(InvalidNameError):
    """
    Raised when a name is empty.
    """


class InvalidCharError(InvalidNameError):
    """
    Raised when includes invalid character(s) within a string.
    """


class InvalidCharWindowsError(InvalidCharError):
    """
    Raised when includes Windows specific invalid character(s) within a string.
    """


class InvalidLengthError(InvalidNameError):
    """
    Raised when a string too long/short.
    """


class ReservedNameError(InvalidNameError):
    """
    Raised when a string is matched a reserved name.
    """


class ValidReservedNameError(ReservedNameError):
    """
    Raised when a string is matched a reserved name.
    However, it can be used as a name.
    """


class InvalidReservedNameError(ReservedNameError):
    """
    Raised when a string is matched a reserved name.
    And the reserved name is invalid as a name.
    """
