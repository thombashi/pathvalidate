# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import itertools
import os.path
import re

from mbstrdecoder import MultiByteStrDecoder

from ._common import _validate_null_string
from ._error import (
    InvalidCharError,
    InvalidCharWindowsError,
    InvalidLengthError,
    InvalidReservedNameError
)


__INVALID_PATH_CHARS = "\0"
__INVALID_FILENAME_CHARS = __INVALID_PATH_CHARS + "/"
__INVALID_WIN_PATH_CHARS = __INVALID_PATH_CHARS + ':*?"<>|'
__INVALID_WIN_FILENAME_CHARS = (
    __INVALID_FILENAME_CHARS +
    __INVALID_WIN_PATH_CHARS +
    "\\"
)

__RE_INVALID_FILENAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_FILENAME_CHARS)), re.UNICODE)
__RE_INVALID_WIN_FILENAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_WIN_FILENAME_CHARS)), re.UNICODE)
__RE_INVALID_PATH = re.compile(
    "[{:s}]".format(re.escape(__INVALID_PATH_CHARS)), re.UNICODE)
__RE_INVALID_WIN_PATH = re.compile(
    "[{:s}]".format(re.escape(__INVALID_WIN_PATH_CHARS)), re.UNICODE)

__WINDOWS_RESERVED_FILE_NAME_LIST = [
    "CON", "PRN", "AUX", "NUL",
] + [
    "{:s}{:d}".format(name, num)
    for name, num in itertools.product(["COM", "LPT"], range(1, 10))
]

__MAX_FILENAME = 255
__LINUX_MAX_PATH = 1024


def validate_filename(filename):
    """
    Verifying whether the ``filename`` is a valid file name or not.

    :param str filename: Filename to validate.
    :raises pathvalidate.NullNameError: If the ``filename`` is empty.
    :raises pathvalidate.InvalidLengthError:
        If the ``filename`` is longer than 255 characters.
    :raises pathvalidate.InvalidCharError:
        If the ``filename`` includes invalid character(s) for a filename:
        |invalid_filename_chars|.
    :raises pathvalidate.InvalidCharWindowsError:
        If the ``filename`` includes invalid character(s) for a Windows
        filename: |invalid_win_filename_chars|
    :raises pathvalidate.InvalidReservedNameError:
        If the ``filename`` equals reserved name by OS

    .. seealso::

        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    _validate_null_string(filename)

    if len(filename) > __MAX_FILENAME:
        raise InvalidLengthError(
            "filename is too long: expected<={:d}, actual={:d}".format(
                __MAX_FILENAME, len(filename)))

    error_message_template = "invalid char found in the filename: '{:s}'"

    unicode_filename = MultiByteStrDecoder(filename).unicode_str
    match = __RE_INVALID_FILENAME.search(unicode_filename)
    if match is not None:
        raise InvalidCharError(
            error_message_template.format(re.escape(match.group())))

    match = __RE_INVALID_WIN_FILENAME.search(unicode_filename)
    if match is not None:
        raise InvalidCharWindowsError(
            error_message_template.format(re.escape(match.group())))

    if unicode_filename.upper() in __WINDOWS_RESERVED_FILE_NAME_LIST:
        raise InvalidReservedNameError(
            "{} is a reserved name by Windows".format(unicode_filename))


def validate_file_path(file_path):
    """
    Verifying whether the ``file_path`` is a valid file path or not.

    :param str file_path: File path to validate.
    :raises pathvalidate.NullNameError: If the ``file_path`` is empty.
    :raises pathvalidate.InvalidCharError:
        If the ``file_path`` includes invalid char(s):
        |invalid_file_path_chars|.
    :raises pathvalidate.InvalidCharWindowsError:
        If the ``file_path`` includes invalid character(s) for a Windows
        file path: |invalid_win_file_path_chars|
    :raises pathvalidate.InvalidLengthError:
        If the ``file_path`` is longer than 1024 characters.

    .. seealso::

        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    _validate_null_string(file_path)

    error_message_template = "invalid char found : invalid-char='{}', path='{}'"

    file_path = os.path.normpath(os.path.splitdrive(file_path)[1])

    unicode_file_path = MultiByteStrDecoder(file_path).unicode_str
    match = __RE_INVALID_PATH.search(unicode_file_path)
    if match is not None:
        raise InvalidCharError(error_message_template.format(
            re.escape(match.group()), unicode_file_path))

    match = __RE_INVALID_WIN_PATH.search(unicode_file_path)
    if match is not None:
        raise InvalidCharWindowsError(error_message_template.format(
            re.escape(match.group()), unicode_file_path))

    if len(unicode_file_path) > __LINUX_MAX_PATH:
        raise InvalidLengthError(
            "file path is too long: expected<={:d}, actual={:d}".format(
                __LINUX_MAX_PATH, len(unicode_file_path)))


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
        unicode_filename = MultiByteStrDecoder(filename.strip()).unicode_str
    except AttributeError as e:
        raise ValueError(e)

    return __RE_INVALID_WIN_FILENAME.sub(
        replacement_text, unicode_filename)


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
        unicode_file_path = MultiByteStrDecoder(file_path.strip()).unicode_str
    except AttributeError as e:
        raise ValueError(e)

    return __RE_INVALID_WIN_PATH.sub(replacement_text, unicode_file_path)
