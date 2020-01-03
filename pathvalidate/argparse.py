"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from argparse import ArgumentTypeError

from ._common import PathType
from ._file import sanitize_filename, sanitize_filepath, validate_filename, validate_filepath
from .error import ValidationError


def filename(value: PathType) -> PathType:
    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filename(value)


def filepath(value: PathType) -> PathType:
    try:
        validate_filepath(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filepath(value)
