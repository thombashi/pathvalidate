# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import enum
import itertools
import os.path
import platform
import re

from ._common import preprocess, unprintable_ascii_chars
from ._interface import NameSanitizer
from ._six import text_type
from .error import InvalidCharError, InvalidLengthError, ReservedNameError


_DEFAULT_MAX_FILENAME_LEN = 255


@enum.unique
class Platform(enum.Enum):
    UNIVERSAL = "universal"
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


class FileSanitizer(NameSanitizer):
    _INVALID_PATH_CHARS = "".join(unprintable_ascii_chars)
    _INVALID_FILENAME_CHARS = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS = _INVALID_PATH_CHARS + ':*?"<>|\t\n\r\x0b\x0c'
    _INVALID_WIN_FILENAME_CHARS = _INVALID_FILENAME_CHARS + _INVALID_WIN_PATH_CHARS + "\\"

    _ERROR_MSG_TEMPLATE = "invalid char found : invalid-char='{}', value='{}'"

    @property
    def platform(self):
        return self.__platform

    @property
    def platform_name(self):
        # Deprecated
        return self.platform

    @property
    def reserved_keywords(self):
        return (".", "..")

    @property
    def max_len(self):
        return self._max_len

    def __init__(self, filename, max_len, platform=None):
        super(FileSanitizer, self).__init__(filename)

        self._max_len = max_len

        self.__platform = self.__normalize_platform(platform)

    def _is_universal(self):
        return self.platform == Platform.UNIVERSAL

    def _is_linux(self):
        return self.platform == Platform.LINUX

    def _is_windows(self):
        return self.platform == Platform.WINDOWS

    def _is_macos(self):
        return self.platform == Platform.MACOS

    def _validate_max_len(self):
        if self.max_len < 1:
            raise ValueError("max_len must be greater or equals to one")

    def _validate_reserved_keywords(self, name):
        if self._is_reserved_keyword(name.upper()):
            raise ReservedNameError(
                "'{}' is a reserved name for {}".format(name, self.platform), reusable_name=False
            )

    def _get_default_max_path_len(self):
        if self._is_linux():
            return 4096

        if self._is_windows():
            return 260

        if self._is_macos():
            return 1024

        return 260  # universal

    @staticmethod
    def __normalize_platform(name):
        if isinstance(name, Platform):
            return name

        if name:
            name = name.strip().lower()

        if name == "auto":
            name = platform.system().lower()

        if name in ["linux"]:
            return Platform.LINUX

        if name and name.startswith("win"):
            return Platform.WINDOWS

        if name in ["mac", "macos", "darwin"]:
            return Platform.MACOS

        return Platform.UNIVERSAL


class FileNameSanitizer(FileSanitizer):

    __WINDOWS_RESERVED_FILE_NAMES = ("CON", "PRN", "AUX", "NUL") + tuple(
        "{:s}{:d}".format(name, num)
        for name, num in itertools.product(("COM", "LPT"), range(1, 10))
    )

    __RE_INVALID_FILENAME = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_FILENAME_CHARS)), re.UNICODE
    )
    __RE_INVALID_WIN_FILENAME = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_WIN_FILENAME_CHARS)), re.UNICODE
    )

    @property
    def reserved_keywords(self):
        common_keywords = super(FileNameSanitizer, self).reserved_keywords

        if self._is_universal() or self._is_windows():
            return common_keywords + self.__WINDOWS_RESERVED_FILE_NAMES

        return common_keywords

    def __init__(self, filename, max_filename_len=_DEFAULT_MAX_FILENAME_LEN, platform=None):
        super(FileNameSanitizer, self).__init__(
            filename,
            max_len=(
                max_filename_len if max_filename_len is not None else _DEFAULT_MAX_FILENAME_LEN
            ),
            platform=platform,
        )

        if self.max_len > self._get_default_max_path_len():
            self._max_len = self._get_default_max_path_len()

        self._validate_max_len()

        self._sanitize_regexp = self._get_sanitize_regexp()

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        is_pathlike_obj = self._is_pathlike_obj()
        sanitized_filename = self._sanitize_regexp.sub(replacement_text, self._str)
        sanitized_filename = sanitized_filename[: self.max_len]

        try:
            self._validate(sanitized_filename)
        except ReservedNameError as e:
            if e.reusable_name is False:
                sanitized_filename += "_"
        except InvalidCharError:
            if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
                sanitized_filename = sanitized_filename.rstrip(" .")

        if is_pathlike_obj:
            try:
                from pathlib import Path

                return Path(sanitized_filename)
            except ImportError:
                pass

        return sanitized_filename

    def _validate(self, value):
        self._validate_null_string(value)

        if len(text_type(value)) > self.max_len:
            raise InvalidLengthError(
                "filename is too long: expected<={:d}, actual={:d}".format(
                    self.max_len, len(text_type(value))
                )
            )

        unicode_filename = preprocess(value)

        self._validate_reserved_keywords(unicode_filename)

        if self._is_universal():
            self.__validate_unix_filename(unicode_filename)
            self.__validate_win_filename(unicode_filename)
        elif self._is_windows():
            self.__validate_win_filename(unicode_filename)
        else:
            self.__validate_unix_filename(unicode_filename)

    def __validate_unix_filename(self, unicode_filename):
        match = self.__RE_INVALID_FILENAME.search(unicode_filename)
        if match is not None:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(unicode_filename, re.escape(match.group()))
            )

    def __validate_win_filename(self, unicode_filename):
        match = self.__RE_INVALID_WIN_FILENAME.search(unicode_filename)
        if match is not None:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(unicode_filename, re.escape(match.group())),
                platform=Platform.WINDOWS,
            )

        if unicode_filename[-1] in (" ", "."):
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(unicode_filename, re.escape(unicode_filename[-1])),
                platform=Platform.WINDOWS,
                description="Do not end a file or directory name with a space or a period",
            )

    def _get_sanitize_regexp(self):
        if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
            return self.__RE_INVALID_WIN_FILENAME

        return self.__RE_INVALID_FILENAME


class FilePathSanitizer(FileSanitizer):

    __RE_INVALID_PATH = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_PATH_CHARS)), re.UNICODE
    )
    __RE_INVALID_WIN_PATH = re.compile(
        "[{:s}]".format(re.escape(FileSanitizer._INVALID_WIN_PATH_CHARS)), re.UNICODE
    )

    def __init__(self, filename, platform=None, max_path_len=None):
        super(FilePathSanitizer, self).__init__(filename, max_len=max_path_len, platform=platform)

        if self.max_len is None:
            self._max_len = self._get_default_max_path_len()

        self._validate_max_len()

        self._sanitize_regexp = self._get_sanitize_regexp()

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        is_pathlike_obj = self._is_pathlike_obj()

        try:
            unicode_file_path = preprocess(self._value)
        except AttributeError as e:
            raise ValueError(e)

        sanitized_path = self._sanitize_regexp.sub(replacement_text, unicode_file_path)

        if is_pathlike_obj:
            try:
                from pathlib import Path

                return Path(sanitized_path)
            except ImportError:
                pass

        return sanitized_path

    def _validate(self, value):
        self._validate_null_string(value)

        value = os.path.splitdrive(value)[1]
        if not value:
            return

        file_path = os.path.normpath(value)
        unicode_file_path = preprocess(file_path)

        self._validate_reserved_keywords(unicode_file_path)

        if self._is_universal():
            self.__validate_unix_file_path(unicode_file_path)
            self.__validate_win_file_path(unicode_file_path)
        elif self._is_windows():
            self.__validate_win_file_path(unicode_file_path)
        else:
            self.__validate_unix_file_path(unicode_file_path)

        if len(unicode_file_path) > self.max_len:
            raise InvalidLengthError(
                "file path is too long: expected<={:d}, actual={:d}".format(
                    self.max_len, len(unicode_file_path)
                )
            )

    def __validate_unix_file_path(self, unicode_file_path):
        match = self.__RE_INVALID_PATH.search(unicode_file_path)
        if match is not None:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(re.escape(match.group()), unicode_file_path)
            )

    def __validate_win_file_path(self, unicode_file_path):
        match = self.__RE_INVALID_WIN_PATH.search(unicode_file_path)
        if match is not None:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(re.escape(match.group()), unicode_file_path),
                platform=Platform.WINDOWS,
            )

    def _get_sanitize_regexp(self):
        if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
            return self.__RE_INVALID_WIN_PATH

        return self.__RE_INVALID_PATH


def validate_filename(filename, platform=None, max_filename_len=_DEFAULT_MAX_FILENAME_LEN):
    """Verifying whether the ``filename`` is a valid file name or not.

    Args:
        filename (str):
            Filename to validate.
        platform (str/pathvalidate.Platform, optional):
            |platform_name|
        max_filename_len (int, optional):
            Length limit of the ``filename``. The value must be lower than:

                - ``Linux``: 4096
                - ``macOS``: 1024
                - ``Windows``: 260
                - ``Universal``: 260

            Defaults to 255.

    Raises:
        InvalidLengthError:
            If the ``filename`` is longer than ``max_filename_len`` characters.
        InvalidCharError:
            If the ``filename`` includes invalid character(s) for a filename:
            |invalid_filename_chars|.
            The following characters are also invalid for Windows platform:
            |invalid_win_filename_chars|.
        ReservedNameError:
            If the ``filename`` equals reserved name by OS.
            Windows reserved name is as follows:
            ``"CON"``, ``"PRN"``, ``"AUX"``, ``"NUL"``, ``"COM[1-9]"``, ``"LPT[1-9]"``.

    Example:
        :ref:`example-validate-filename`

    See Also:
        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FileNameSanitizer(filename, platform=platform, max_filename_len=max_filename_len).validate()


def validate_filepath(file_path, platform=None, max_path_len=None):
    """Verifying whether the ``file_path`` is a valid file path or not.
    
    Args:
        file_path (str):
            File path to validate.
        platform (str/pathvalidate.Platform, optional):
            |platform_name|
        max_path_len (int, optional):
            The upper limit of the ``file_path`` length. If the value is |None|,
            in the default, automatically determined by the ``platform``:

                - ``Linux``: 4096
                - ``macOS``: 1024
                - ``Windows``: 260

    Raises:
        NullNameError:
            If the ``file_path`` is empty.
        InvalidCharError:
            If the ``file_path`` includes invalid char(s):
            |invalid_file_path_chars|.
            The following characters are also invalid for Windows platform:
            |invalid_win_file_path_chars|
        InvalidLengthError:
            If the ``file_path`` is longer than ``max_path_len`` characters.

    Example:
        :ref:`example-validate-file-path`

    See Also:
        `Naming Files, Paths, and Namespaces (Windows)
        <https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx>`__
    """

    FilePathSanitizer(file_path, platform=platform, max_path_len=max_path_len).validate()


def validate_file_path(file_path, platform=None, max_path_len=None):
    # Deprecated
    validate_filepath(file_path, platform, max_path_len)


def sanitize_filename(
    filename, replacement_text="", platform=None, max_filename_len=_DEFAULT_MAX_FILENAME_LEN
):
    """
    Make a valid filename from a string.

    To make a valid filename the function does:

    - Replace invalid characters for a filename within the ``filename``
      with the ``replacement_text``.
      Invalid characters are as followings and unprintable characters:
      |invalid_filename_chars|, (for Windows: |invalid_win_filename_chars|).
    - Append underscore (``"_"``) at the tail of the name if sanitized name
      is one of the reserved names by the OS.

    :param filename: Filename to sanitize.
    :type filename: str or PathLike object
    :param str replacement_text: Replacement text.
    :param str platform: |platform_name|
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
        filename, platform=platform, max_filename_len=max_filename_len
    ).sanitize(replacement_text)


def sanitize_filepath(file_path, replacement_text="", platform=None, max_path_len=None):
    """Make a valid file path from a string.

    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``.
    Invalid characters are as followings:
    |invalid_file_path_chars|, |invalid_win_file_path_chars| (and non printable characters).

    Args:
        file_path (str or PathLike object):
            File path to sanitize.
        replacement_text (str, optional):
            Replacement text for invalid characters.
            Defaults to ``""``.
        platform (str/pathvalidate.Platform, optional):
            |platform_name|
        max_path_len (int, optional):
            The upper limit of the ``file_path`` length. Truncate the name if the ``file_path``
            length exceedd this value. If the value is |None|, the default value automatically
            determined by the execution platform:

                - ``Linux``: 4096
                - ``macOS``: 1024
                - ``Windows``: 260

    Returns:
        Same type as the argument (str or PathLike object):
            Sanitized filepath.

    Raises:
        ValueError:
            If the ``file_path`` is an invalid file path.

    Example:
        :ref:`example-sanitize-file-path`
    """

    return FilePathSanitizer(file_path, platform=platform, max_path_len=max_path_len).sanitize(
        replacement_text
    )


def sanitize_file_path(file_path, replacement_text="", platform=None, max_path_len=None):
    # Deprecated
    return sanitize_filepath(file_path, platform, max_path_len)
