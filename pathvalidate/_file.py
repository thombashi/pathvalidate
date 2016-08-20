# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

from ._common import _validate_null_string
from ._error import InvalidCharError


__INVALID_PATH_CHARS = '\:*?"<>|'
__INVALID_FILENAME_CHARS = __INVALID_PATH_CHARS + "/"

__RE_INVALID_FILENAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_FILENAME_CHARS)))
__RE_INVALID_PATH = re.compile(
    "[{:s}]".format(re.escape(__INVALID_PATH_CHARS)))


def validate_filename(filename):
    """
    :param str filename: Filename to validate.
    :raises ValueError:
        If the ``filename`` is empty or includes invalid char(s):
        |invalid_filename_chars|.
    """

    _validate_null_string(filename)

    match = __RE_INVALID_FILENAME.search(filename)
    if match is not None:
        raise InvalidCharError(
            "invalid char found in the filename: '{:s}'".format(
                re.escape(match.group())))


def validate_file_path(file_path):
    """
    :param str filename: File path to validate.
    :raises ValueError:
        If the ``file_path`` is empty or includes invalid char(s):
        |invalid_file_path_chars|.
    """

    _validate_null_string(file_path)

    match = __RE_INVALID_PATH.search(file_path)
    if match is not None:
        raise InvalidCharError(
            "invalid char found in the file path: '{:s}'".format(
                re.escape(match.group())))


def sanitize_filename(filename, replacement_text=""):
    """
    Replace invalid characters for a filename within the ``filename``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_filename_chars|.

    :param str filename: Filename to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``filename`` is a invalid filename.
    """

    try:
        return __RE_INVALID_FILENAME.sub(replacement_text, filename.strip())
    except AttributeError as e:
        raise ValueError(e)


def sanitize_file_path(file_path, replacement_text=""):
    """
    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_file_path_chars|.

    :param str file_path: File path to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``file_path`` is a invalid file path.
    """

    try:
        return __RE_INVALID_PATH.sub(replacement_text, file_path.strip())
    except AttributeError as e:
        raise ValueError(e)
