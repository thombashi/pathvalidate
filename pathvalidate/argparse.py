# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from argparse import ArgumentTypeError

from ._file import sanitize_filename, sanitize_filepath, validate_filename, validate_filepath
from .error import ValidationError


def filename(value):
    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filename(value)


def filepath(value):
    try:
        validate_filepath(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filepath(value)
