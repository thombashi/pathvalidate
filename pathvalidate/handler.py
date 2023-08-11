"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from datetime import datetime
from typing import Callable

from .error import ValidationError


NullValueHandler = Callable[[ValidationError], str]


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
