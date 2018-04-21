# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals


class NameError(ValueError):
    """
    Base exception class that indicates invalid name errors.
    """


class NullNameError(NameError):
    """
    Exception raised when a name is empty.
    """


class InvalidCharError(NameError):
    """
    Exception raised when includes invalid character(s) within a string.
    """


class InvalidCharWindowsError(InvalidCharError):
    """
    Exception raised when includes Windows specific invalid character(s)
    within a string.
    """


class InvalidLengthError(NameError):
    """
    Exception raised when a string too long/short.
    """


class ReservedNameError(NameError):
    """
    Exception raised when a string matched a reserved name.
    """


class ValidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    However, it can be used as a name.
    """


class InvalidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    Moreover, the reserved name is invalid as a name.
    """
