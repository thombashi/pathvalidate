# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import itertools
import os.path
import platform
import re

from mbstrdecoder import MultiByteStrDecoder

from ._common import NameSanitizer
from ._error import (
    InvalidCharError,
    InvalidCharWindowsError,
    InvalidLengthError,
    InvalidReservedNameError
)


class FileSanitizer(NameSanitizer):
    _VALID_WIN_PLATFORM_NAME_LIST = ["windows", "win"]

    _INVALID_PATH_CHARS = "\0"
    _INVALID_FILENAME_CHARS = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS = _INVALID_PATH_CHARS + ':*?"<>|'
    _INVALID_WIN_FILENAME_CHARS = (
        _INVALID_FILENAME_CHARS +
        _INVALID_WIN_PATH_CHARS +
        "\\"
    )

    _ERROR_MSG_TEMPLATE = "invalid char found : invalid-char='{}', value='{}'"

    @property
    def platform_name(self):
        if self._platform_name is None:
            platform_name = platform.system()
        else:
            platform_name = self._platform_name

        return platform_name.lower()

    def __init__(self, filename, platform_name=None):
        super(FileSanitizer, self).__init__(filename)

        self._platform_name = platform_name


class FileNameSanitizer(FileSanitizer):

    __MAX_FILENAME_LEN = 255

    __WINDOWS_RESERVED_FILE_NAME_LIST = [
        "CON", "PRN", "AUX", "NUL",
    ] + [
        "{:s}{:d}".format(name, num)
        for name, num in itertools.product(["COM", "LPT"], range(1, 10))
    ]

    __RE_INVALID_FILENAME = re.compile("[{:s}]".format(
        re.escape(FileSanitizer._INVALID_FILENAME_CHARS)), re.UNICODE)
    __RE_INVALID_WIN_FILENAME = re.compile("[{:s}]".format(
        re.escape(FileSanitizer._INVALID_WIN_FILENAME_CHARS)), re.UNICODE)

    @property
    def reserved_keywords(self):
        return self.__WINDOWS_RESERVED_FILE_NAME_LIST

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        sanitize_file_name = self.__RE_INVALID_WIN_FILENAME.sub(
            replacement_text, self._unicode_str)

        try:
            self._validate(sanitize_file_name)
        except InvalidReservedNameError:
            sanitize_file_name += "_"

        return sanitize_file_name

    def _validate(self, value):
        self._validate_null_string(value)

        if len(value) > self.__MAX_FILENAME_LEN:
            raise InvalidLengthError(
                "filename is too long: expected<={:d}, actual={:d}".format(
                    self.__MAX_FILENAME_LEN, len(value)))

        error_message_template = "invalid char found in the filename: '{:s}'"
        unicode_filename = MultiByteStrDecoder(value).unicode_str

        if self.platform_name in self._VALID_WIN_PLATFORM_NAME_LIST:
            self.__validate_win_filename(unicode_filename)
        else:
            match = self.__RE_INVALID_FILENAME.search(unicode_filename)
            if match is not None:
                raise InvalidCharError(
                    error_message_template.format(re.escape(match.group())))

    def __validate_win_filename(self, unicode_filename):
        match = self.__RE_INVALID_WIN_FILENAME.search(unicode_filename)
        if match is not None:
            raise InvalidCharWindowsError(self._ERROR_MSG_TEMPLATE.format(
                unicode_filename, re.escape(match.group())))

        if self._is_reserved_keyword(unicode_filename.upper()):
            raise InvalidReservedNameError(
                "{} is a reserved name by Windows".format(unicode_filename))


class FilePathSanitizer(FileSanitizer):

    __RE_INVALID_PATH = re.compile("[{:s}]".format(
        re.escape(FileSanitizer._INVALID_PATH_CHARS)), re.UNICODE)
    __RE_INVALID_WIN_PATH = re.compile("[{:s}]".format(
        re.escape(FileSanitizer._INVALID_WIN_PATH_CHARS)), re.UNICODE)

    __LINUX_MAX_PATH = 1024

    @property
    def reserved_keywords(self):
        return []

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        try:
            unicode_file_path = MultiByteStrDecoder(
                self._value.strip()).unicode_str
        except AttributeError as e:
            raise ValueError(e)

        return self.__RE_INVALID_WIN_PATH.sub(
            replacement_text, unicode_file_path)

    def _validate(self, value):
        self._validate_null_string(value)

        file_path = os.path.normpath(os.path.splitdrive(value)[1])
        unicode_file_path = MultiByteStrDecoder(file_path).unicode_str

        if self.platform_name in self._VALID_WIN_PLATFORM_NAME_LIST:
            self.__validate_win_file_path(unicode_file_path)
        else:
            match = self.__RE_INVALID_PATH.search(unicode_file_path)
            if match is not None:
                raise InvalidCharError(self._ERROR_MSG_TEMPLATE.format(
                    re.escape(match.group()), unicode_file_path))

        if len(unicode_file_path) > self.__LINUX_MAX_PATH:
            raise InvalidLengthError(
                "file path is too long: expected<={:d}, actual={:d}".format(
                    self.__LINUX_MAX_PATH, len(unicode_file_path)))

    def __validate_win_file_path(self, unicode_file_path):
        match = self.__RE_INVALID_WIN_PATH.search(unicode_file_path)
        if match is not None:
            raise InvalidCharWindowsError(self._ERROR_MSG_TEMPLATE.format(
                re.escape(match.group()), unicode_file_path))


def validate_filename(filename, platform_name=None):
    """
    Verifying whether the ``filename`` is a valid file name or not.

    :param str filename: Filename to validate.
    :param str platform_name:
        Execution platform name.
        Available palatforms are ``"Linux"`` or ``"Windows"``.
        Defaults to |None| (automatically detect platform).
    :raises pathvalidate.NullNameError: If the ``filename`` is empty.
    :raises pathvalidate.InvalidLengthError:
        If the ``filename`` is longer than 255 characters.
    :raises pathvalidate.InvalidCharError:
        If the ``filename`` includes invalid character(s) for a filename:
        |invalid_filename_chars|.
    :raises pathvalidate.InvalidCharWindowsError:
        If the ``filename`` includes invalid character(s) for a Windows
        filename: |invalid_win_filename_chars|.
    :raises pathvalidate.InvalidReservedNameError:
        If the ``filename`` equals reserved name by OS.
        Windows reserved name is as follows:
        ``"CON"``, ``"PRN"``, ``"AUX"``, ``"NUL"``,
        ``"COM[1-9]"``, ``"LPT[1-9]"``

    :Examples:

        :ref:`example-validate-filename`

    .. seealso::

        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FileNameSanitizer(filename, platform_name).validate()


def validate_file_path(file_path, platform_name=None):
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

    :Examples:

        :ref:`example-validate-file-path`

    .. seealso::

        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FilePathSanitizer(file_path, platform_name).validate()


def sanitize_filename(filename, replacement_text=""):
    """
    Make a valid filename for both Windows and Linux.

    To make a valid filename:

    - Replace invalid characters for a filename within the ``filename``
      with the ``replacement_text``. Invalid characters are as follows:
      |invalid_filename_chars|, |invalid_win_filename_chars|.
    - Append under bar (``"_"``) at the tail of the name if sanitized name
      is one of the reserved names by the OS.

    :param str filename: Filename to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``filename`` is a invalid filename.

    :Examples:

        :ref:`example-sanitize-filename`

    .. note::

        Reserved names by OS will not be replaced.
    """

    return FileNameSanitizer(filename).sanitize(replacement_text)


def sanitize_file_path(file_path, replacement_text=""):
    """
    Make a valid file path for both Windows and Linux.
    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_file_path_chars|, |invalid_win_file_path_chars|.

    :param str file_path: File path to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``file_path`` is a invalid file path.

    :Examples:

        :ref:`example-sanitize-file-path`
    """

    return FilePathSanitizer(file_path).sanitize(replacement_text)
