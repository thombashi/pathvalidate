# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import click

from ._file import sanitize_filename, sanitize_filepath, validate_filename, validate_filepath
from .error import ValidationError


def filename(ctx, param, value):
    if not value:
        return None

    try:
        validate_filename(value)
    except ValidationError as e:
        raise click.BadParameter(e)

    return sanitize_filename(value)


def filepath(ctx, param, value):
    if not value:
        return None

    try:
        validate_filepath(value)
    except ValidationError as e:
        raise click.BadParameter(e)

    return sanitize_filepath(value)
