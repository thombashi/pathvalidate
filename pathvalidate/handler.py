"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from datetime import datetime
from typing import Callable

from .error import ValidationError


ValidationErrorHandler = Callable[[ValidationError], str]


def return_null_string(e: ValidationError) -> str:
    """Null value handler that always returns an empty string.

    Args:
        e (ValidationError): A validation error.

    Returns:
        str: An empty string.
    """

    return ""


def return_timestamp(e: ValidationError) -> str:
    """Null value handler that returns a timestamp of when the function was called.

    Args:
        e (ValidationError): A validation error.

    Returns:
        str: A timestamp.
    """

    return str(datetime.now().timestamp())


def raise_error(e: ValidationError) -> str:
    """Null value handler that always raises an exception.

    Args:
        e (ValidationError): A validation error.

    Raises:
        ValidationError: Always raised.
    """

    raise e


class ReservedNameHandler:
    @classmethod
    def add_leading_underscore(cls, e: ValidationError) -> str:
        """Reserved name handler that adds a leading underscore (``"_"``) to the name
        except for ``"."`` and ``".."``.

        Args:
            e (ValidationError): A reserved name error.

        Returns:
            str: The converted name.
        """

        if e.reserved_name in (".", "..") or e.reusable_name:
            return e.reserved_name

        return f"_{e.reserved_name}"

    @classmethod
    def add_trailing_underscore(cls, e: ValidationError) -> str:
        """Reserved name handler that adds a trailing underscore (``"_"``) to the name
        except for ``"."`` and ``".."``.

        Args:
            e (ValidationError): A reserved name error.

        Returns:
            str: The converted name.
        """

        if e.reserved_name in (".", "..") or e.reusable_name:
            return e.reserved_name

        return f"{e.reserved_name}_"

    @classmethod
    def as_is(cls, e: ValidationError) -> str:
        """Reserved name handler that returns the name as is.

        Args:
            e (ValidationError): A reserved name error.

        Returns:
            str: The name as is.
        """

        return e.reserved_name

    @classmethod
    def raise_error(cls, e: ValidationError) -> str:
        """Reserved name handler that always raises an exception.

        Args:
            e (ValidationError): A reserved name error.

        Raises:
            ValidationError: Always raised.
        """

        raise e
