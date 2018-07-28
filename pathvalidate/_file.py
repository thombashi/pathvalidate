# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import itertools
import os.path
import platform
import re

from ._common import _preprocess, unprintable_ascii_char_list
from ._interface import NameSanitizer
from ._six import text_type
from .error import (
    InvalidCharError,
    InvalidCharWindowsError,
    InvalidLengthError,
    InvalidReservedNameError,
)


_DEFAULT_MAX_FILENAME_LEN = 255


class FileSanitizer(NameSanitizer):
    _INVALID_PATH_CHARS = "".join(unprintable_ascii_char_list)
    _INVALID_FILENAME_CHARS = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS = _INVALID_PATH_CHARS + ':*?"<>|'
    _INVALID_WIN_FILENAME_CHARS = _INVALID_FILENAME_CHARS + _INVALID_WIN_PATH_CHARS + "\\"

    _ERROR_MSG_TEMPLATE = "invalid char found : invalid-char='{}', value='{}'"

    @property
    def platform_name(self):
        return self.__platform_name

    @property
    def max_len(self):
        return self._max_len

    def __init__(self, filename, max_len, platform_name=None):
        super(FileSanitizer, self).__init__(filename)

        self._max_len = max_len

        if platform_name is None:
            platform_name = platform.system()

        self.__platform_name = platform_name.lower()

    def _is_linux(self):
        return self.platform_name in ["linux"]

    def _is_windows(self):
        return self.platform_name in ["windows", "win"]

    def _is_macos(self):
        return self.platform_name in ["mac", "macos", "darwin"]


class FileNameSanitizer(FileSanitizer):

    __WINDOWS_RESERVED_FILE_NAME_LIST = ["CON", "PRN", "AUX", "NUL"] + [
        "{:s}{:d}".format(name, num)
        for name, num in itertools.product(["COM", "LPT"], range(1, 10))
    ]

    __RE_INVALID_FILENAME = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_FILENAME_CHARS)), re.UNICODE
    )
    __RE_INVALID_WIN_FILENAME = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_WIN_FILENAME_CHARS)), re.UNICODE
    )

    @property
    def reserved_keywords(self):
        return self.__WINDOWS_RESERVED_FILE_NAME_LIST

    def __init__(self, filename, max_filename_len=_DEFAULT_MAX_FILENAME_LEN, platform_name=None):
        super(FileNameSanitizer, self).__init__(
            filename, max_len=max_filename_len, platform_name=platform_name
        )

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        is_pathlike_obj = self._is_pathlike_obj()
        sanitize_file_name = self.__RE_INVALID_WIN_FILENAME.sub(replacement_text, self._str)
        sanitize_file_name = sanitize_file_name[: self.max_len]

        try:
            self._validate(sanitize_file_name)
        except InvalidReservedNameError:
            sanitize_file_name += "_"

        if is_pathlike_obj:
            try:
                from pathlib import Path

                return Path(sanitize_file_name)
            except ImportError:
                pass

        return sanitize_file_name

    def _validate(self, value):
        self._validate_null_string(value)

        if len(text_type(value)) > self.max_len:
            raise InvalidLengthError(
                "filename is too long: expected<={:d}, actual={:d}".format(
                    self.max_len, len(text_type(value))
                )
            )

        error_message_template = "invalid char found in the filename: '{:s}'"
        unicode_filename = _preprocess(value)

        if self._is_windows():
            self.__validate_win_filename(unicode_filename)
        else:
            match = self.__RE_INVALID_FILENAME.search(unicode_filename)
            if match is not None:
                raise InvalidCharError(error_message_template.format(re.escape(match.group())))

    def __validate_win_filename(self, unicode_filename):
        match = self.__RE_INVALID_WIN_FILENAME.search(unicode_filename)
        if match is not None:
            raise InvalidCharWindowsError(
                self._ERROR_MSG_TEMPLATE.format(unicode_filename, re.escape(match.group()))
            )

        if self._is_reserved_keyword(unicode_filename.upper()):
            raise InvalidReservedNameError(
                "{} is a reserved name by Windows".format(unicode_filename)
            )


class FilePathSanitizer(FileSanitizer):

    __RE_INVALID_PATH = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_PATH_CHARS)), re.UNICODE
    )
    __RE_INVALID_WIN_PATH = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_WIN_PATH_CHARS)), re.UNICODE
    )

    @property
    def reserved_keywords(self):
        return []

    def __init__(self, filename, platform_name=None, max_path_len=None):
        super(FilePathSanitizer, self).__init__(
            filename, max_len=max_path_len, platform_name=platform_name
        )

        if self.max_len is None:
            self._max_len = self.__get_default_max_path_len()

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        is_pathlike_obj = self._is_pathlike_obj()

        try:
            unicode_file_path = _preprocess(self._value)
        except AttributeError as e:
            raise ValueError(e)

        sanitized_path = self.__RE_INVALID_WIN_PATH.sub(replacement_text, unicode_file_path)

        if is_pathlike_obj:
            try:
                from pathlib import Path

                return Path(sanitized_path)
            except ImportError:
                pass

        return sanitized_path

    def _validate(self, value):
        self._validate_null_string(value)

        file_path = os.path.normpath(os.path.splitdrive(value)[1])
        unicode_file_path = _preprocess(file_path)

        if self._is_windows():
            self.__validate_win_file_path(unicode_file_path)
        else:
            match = self.__RE_INVALID_PATH.search(unicode_file_path)
            if match is not None:
                raise InvalidCharError(
                    self._ERROR_MSG_TEMPLATE.format(re.escape(match.group()), unicode_file_path)
                )

        if len(unicode_file_path) > self.max_len:
            raise InvalidLengthError(
                "file path is too long: expected<={:d}, actual={:d}".format(
                    self.max_len, len(unicode_file_path)
                )
            )

    def __get_default_max_path_len(self):
        if self._is_linux():
            return 4096

        if self._is_windows():
            return 260

        if self._is_macos():
            return 1024

        return 260

    def __validate_win_file_path(self, unicode_file_path):
        match = self.__RE_INVALID_WIN_PATH.search(unicode_file_path)
        if match is not None:
            raise InvalidCharWindowsError(
                self._ERROR_MSG_TEMPLATE.format(re.escape(match.group()), unicode_file_path)
            )


def validate_filename(filename, platform_name=None, max_filename_len=_DEFAULT_MAX_FILENAME_LEN):
    """
    Verifying whether the ``filename`` is a valid file name or not.

    :param str filename: Filename to validate.
    :param str platform_name: |platform_name|
    :param int max_filename_len:
        Upper limit of the ``filename`` length. Defaults to 255.
    :raises pathvalidate.NullNameError: If the ``filename`` is empty.
    :raises pathvalidate.InvalidLengthError:
        If the ``filename`` is longer than ``max_filename_len`` characters.
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

    :Example:
        :ref:`example-validate-filename`

    .. seealso::
        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FileNameSanitizer(
        filename, platform_name=platform_name, max_filename_len=max_filename_len
    ).validate()


def validate_filepath(file_path, platform_name=None, max_path_len=None):
    """
    Verifying whether the ``file_path`` is a valid file path or not.

    :param str file_path: File path to validate.
    :param str platform_name: |platform_name|
    :param int max_filename_len:
        The upper limit of the ``file_path`` length. If the value is |None|,
        the default value automatically determined by the execution
        environment: **(1)** 4096 (``Linux``) **(2)** 260 (``Windows``).
    :raises pathvalidate.NullNameError: If the ``file_path`` is empty.
    :raises pathvalidate.InvalidCharError:
        If the ``file_path`` includes invalid char(s):
        |invalid_file_path_chars|.
    :raises pathvalidate.InvalidCharWindowsError:
        If the ``file_path`` includes invalid character(s) for a Windows
        file path: |invalid_win_file_path_chars|
    :raises pathvalidate.InvalidLengthError:
        If the ``file_path`` is longer than 1024 characters.

    :Example:
        :ref:`example-validate-file-path`

    .. seealso::
        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FilePathSanitizer(file_path, platform_name=platform_name, max_path_len=max_path_len).validate()


def validate_file_path(file_path, platform_name=None, max_path_len=None):
    # [Deprecated]
    validate_filepath(file_path, platform_name, max_path_len)


def sanitize_filename(
    filename, replacement_text="", platform_name=None, max_filename_len=_DEFAULT_MAX_FILENAME_LEN
):
    """
    Make a valid filename for both Windows/Linux/macOS.

    To make a valid filename:

    - Replace invalid characters for a filename within the ``filename``
      with the ``replacement_text``.
      Invalid characters are as followings and unprintable characters:
      |invalid_filename_chars|, |invalid_win_filename_chars|.
    - Append underscore (``"_"``) at the tail of the name if sanitized name
      is one of the reserved names by the OS.

    :param filename: Filename to sanitize.
    :type filename: str or PathLike object
    :param str replacement_text: Replacement text.
    :param str platform_name: |platform_name|
    :param int max_filename_len:
        The upper limit of the ``filename`` length. Truncate the name length if
        the ``filename`` length exceeds this value.
        Defaults to 255.
    :return: Sanitized filename.
    :rtype: Same type as the argument (str or PathLike object)
    :raises ValueError: If the ``filename`` is an invalid filename.

    :Example:
        :ref:`example-sanitize-filename`

    .. note::
        Reserved names by OS not be replaced.
    """

    return FileNameSanitizer(
        filename, platform_name=platform_name, max_filename_len=max_filename_len
    ).sanitize(replacement_text)


def sanitize_filepath(file_path, replacement_text="", platform_name=None, max_path_len=None):
    """
    Make a valid file path for both Windows and Linux.
    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``.
    Invalid characters are as followings and unprintable characters:
    |invalid_file_path_chars|, |invalid_win_file_path_chars|.

    :param file_path: File path to sanitize.
    :type file_path: str or PathLike object
    :param str replacement_text: Replacement text.
    :param str platform_name: |platform_name|
    :param int max_path_len:
        The upper limit of the ``file_path`` length. Truncate the name length
        if the ``file_path`` length exceedd this value.
        If the value is |None|, the default value automatically
        determined by the execution environment:
        **(1)** 4096 (``Linux``)
        **(2)** 260 (``Windows``)
        **(3)** 1024 (``macOS``)
    :return: Sanitized filepath.
    :rtype: Same type as the argument (str or PathLike object)
    :raises ValueError: If the ``file_path`` is an invalid file path.

    :Example:
        :ref:`example-sanitize-file-path`
    """

    return FilePathSanitizer(
        file_path, platform_name=platform_name, max_path_len=max_path_len
    ).sanitize(replacement_text)


def sanitize_file_path(file_path, replacement_text="", platform_name=None, max_path_len=None):
    # [Deprecated]
    return sanitize_filepath(file_path, platform_name, max_path_len)
