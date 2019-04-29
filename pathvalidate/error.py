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
    def platform(self):
        return self.__platform

    @property
    def reason(self):
        return self.__reason

    @property
    def description(self):
        return self.__description

    @property
    def reusable_name(self):
        return self.__reusable_name

    def __init__(self, *args, **kwargs):
        self.__platform = kwargs.pop("platform", None)
        self.__reason = kwargs.pop("reason", None)
        self.__description = kwargs.pop("description", None)
        self.__reusable_name = kwargs.pop("reusable_name", None)

        super(ValidationError, self).__init__(*args[0], **kwargs)

    def __str__(self, *args, **kwargs):
        item_list = [Exception.__str__(self, *args, **kwargs)]

        if self.reason:
            item_list.append("reason={}".format(self.reason.value))
        if self.description:
            item_list.append("description={}".format(self.description))
        if self.reusable_name:
            item_list.append("reusable_name={}".format(self.reusable_name))

        return ", ".join(item_list).strip()

    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)


class NullNameError(ValidationError):
    """
    Exception raised when a name is empty.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.NULL_NAME

        super(NullNameError, self).__init__(args, **kwargs)


class InvalidCharError(ValidationError):
    """
    Exception raised when includes invalid character(s) within a string.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.INVALID_CHARACTER

        super(InvalidCharError, self).__init__(args, **kwargs)


class InvalidLengthError(ValidationError):
    """
    Exception raised when a string too long/short.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reason"] = ErrorReason.INVALID_LENGTH

        super(InvalidLengthError, self).__init__(args, **kwargs)


class ReservedNameError(ValidationError):
    """
    Exception raised when a string matched a reserved name.
    """

    @property
    def reserved_name(self):
        return self.__reserved_name

    def __init__(self, *args, **kwargs):
        self.__reserved_name = kwargs.pop("reserved_name", None)

        kwargs["reason"] = ErrorReason.RESERVED_NAME

        super(ReservedNameError, self).__init__(args, **kwargs)


class ValidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    However, it can be used as a name.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reusable_name"] = True

        super(ValidReservedNameError, self).__init__(args, **kwargs)


class InvalidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    Moreover, the reserved name is invalid as a name.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reusable_name"] = False

        super(InvalidReservedNameError, self).__init__(args, **kwargs)
