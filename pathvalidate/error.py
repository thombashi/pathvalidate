# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import enum


@enum.unique
class ErrorReason(enum.Enum):
    NULL_NAME = "NULL_NAME"
    INVALID_CHARACTER = "INVALID_CHARACTER"
    INVALID_LENGTH = "INVALID_LENGTH"
    RESERVED_NAME = "RESERVED_NAME"


class ValidationError(ValueError):
    """
    Base exception class that indicates invalid name errors.
    """

    @property
    def reason(self):
        return self.__reason

    @property
    def description(self):
        return self.__description

    def __init__(self, *args, **kwargs):
        self.__reason = kwargs.pop("reason", None)
        self.__description = kwargs.pop("description", None)

        super(ValidationError, self).__init__(*args, **kwargs)


class NullNameError(ValidationError):
    """
    Exception raised when a name is empty.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.NULL_NAME

        super(NullNameError, self).__init__(args, kwargs)


class InvalidCharError(ValidationError):
    """
    Exception raised when includes invalid character(s) within a string.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.INVALID_CHARACTER

        super(InvalidCharError, self).__init__(args, kwargs)


class InvalidCharWindowsError(InvalidCharError):
    """
    Exception raised when includes Windows specific invalid character(s)
    within a string.
    """


class InvalidLengthError(ValidationError):
    """
    Exception raised when a string too long/short.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.INVALID_LENGTH

        super(InvalidLengthError, self).__init__(args, kwargs)


class ReservedNameError(ValidationError):
    """
    Exception raised when a string matched a reserved name.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.RESERVED_NAME

        super(ReservedNameError, self).__init__(args, kwargs)


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
