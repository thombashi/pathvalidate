"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum
from typing import Optional

from ._const import Platform


def _to_error_code(code: int) -> str:
    return f"PV{code:04d}"


@enum.unique
class ErrorReason(enum.Enum):
    """
    Validation error reasons.
    """

    NULL_NAME = (_to_error_code(1001), "NULL_NAME", "the value must not be an empty")
    RESERVED_NAME = (
        _to_error_code(1002),
        "RESERVED_NAME",
        "found a reserved name by a platform",
    )
    INVALID_CHARACTER = (
        _to_error_code(1100),
        "INVALID_CHARACTER",
        "invalid characters found",
    )
    INVALID_LENGTH = (
        _to_error_code(1101),
        "INVALID_LENGTH",
        "found an invalid string length",
    )
    FOUND_ABS_PATH = (
        _to_error_code(1200),
        "FOUND_ABS_PATH",
        "found an absolute path where must be a relative path",
    )
    MALFORMED_ABS_PATH = (
        _to_error_code(1201),
        "MALFORMED_ABS_PATH",
        "found a malformed absolute path",
    )
    INVALID_AFTER_SANITIZE = (
        _to_error_code(2000),
        "INVALID_AFTER_SANITIZE",
        "found invalid value after sanitizing",
    )

    @property
    def code(self) -> str:
        return self.__code

    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, code: str, name: str, description: str) -> None:
        self.__name = name
        self.__code = code
        self.__description = description

    def __str__(self) -> str:
        return f"[{self.__code}] {self.__description}"


class ValidationError(ValueError):
    """
    Exception class of validation errors.

    .. py:attribute:: reason

        The cause of the error.

        Returns:
            :py:class:`~pathvalidate.error.ErrorReason`:
    """

    @property
    def platform(self) -> Optional[Platform]:
        return self.__platform

    @property
    def reason(self) -> Optional[ErrorReason]:
        return self.__reason

    @property
    def description(self) -> Optional[str]:
        return self.__description

    @property
    def reserved_name(self) -> str:
        return self.__reserved_name

    @property
    def reusable_name(self) -> Optional[bool]:
        return self.__reusable_name

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self.__platform: Optional[Platform] = kwargs.pop("platform", None)
        self.__reason: Optional[ErrorReason] = kwargs.pop("reason", None)
        self.__description: Optional[str] = kwargs.pop("description", None)
        self.__reserved_name: str = kwargs.pop("reserved_name", "")
        self.__reusable_name: Optional[bool] = kwargs.pop("reusable_name", None)
        self.__fs_encoding: Optional[str] = kwargs.pop("fs_encoding", None)

        try:
            super().__init__(*args[0], **kwargs)
        except IndexError:
            super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        item_list = []
        header = ""

        if self.reason:
            header = str(self.reason)

        if Exception.__str__(self):
            item_list.append(Exception.__str__(self))

        if self.platform:
            item_list.append(f"target-platform={self.platform.value}")
        if self.description:
            item_list.append(f"description={self.description}")
        if self.__reusable_name is not None:
            item_list.append(f"reusable_name={self.reusable_name}")
        if self.__fs_encoding:
            item_list.append(f"fs-encoding={self.__fs_encoding}")

        if item_list:
            header += ": "

        return header + ", ".join(item_list).strip()

    def __repr__(self, *args, **kwargs) -> str:
        return self.__str__(*args, **kwargs)


class NullNameError(ValidationError):
    """
    Exception raised when a name is empty.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs["reason"] = ErrorReason.NULL_NAME

        super().__init__(args, **kwargs)


class InvalidCharError(ValidationError):
    """
    Exception raised when includes invalid character(s) within a string.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        kwargs["reason"] = ErrorReason.INVALID_CHARACTER

        super().__init__(args, **kwargs)


class ReservedNameError(ValidationError):
    """
    Exception raised when a string matched a reserved name.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        kwargs["reason"] = ErrorReason.RESERVED_NAME

        super().__init__(args, **kwargs)


class ValidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    However, it can be used as a name.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        kwargs["reusable_name"] = True

        super().__init__(args, **kwargs)


class InvalidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    Moreover, the reserved name is invalid as a name.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        kwargs["reusable_name"] = False

        super().__init__(args, **kwargs)
