"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from argparse import ArgumentTypeError

from ._common import PathType
from ._file import sanitize_filename, sanitize_filepath, validate_filename, validate_filepath
from .error import ValidationError


def validate_filename_arg(value: str) -> None:
    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)


def validate_filepath_arg(value: str) -> None:
    try:
        validate_filepath(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)


def sanitize_filename_arg(value: str) -> PathType:
    return sanitize_filename(value)


def sanitize_filepath_arg(value: str) -> PathType:
    return sanitize_filepath(value)


def filename(value: PathType) -> PathType:
    # Deprecated
    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filename(value)


def filepath(value: PathType) -> PathType:
    # Deprecated
    try:
        validate_filepath(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filepath(value)
