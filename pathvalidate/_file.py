"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import itertools
import ntpath
import os.path
import platform
import posixpath
import re
from pathlib import Path
from typing import Any, List, Optional, Pattern, Tuple, Union, cast

from ._common import PathType, Platform, is_pathlike_obj, preprocess, unprintable_ascii_chars
from ._interface import NameSanitizer
from .error import (
    ErrorReason,
    InvalidCharError,
    InvalidLengthError,
    ReservedNameError,
    ValidationError,
)


_DEFAULT_MAX_FILENAME_LEN = 255
_NTFS_RESERVED_FILE_NAMES = (
    "$Mft",
    "$MftMirr",
    "$LogFile",
    "$Volume",
    "$AttrDef",
    "$Bitmap",
    "$Boot",
    "$BadClus",
    "$Secure",
    "$Upcase",
    "$Extend",
    "$Quota",
    "$ObjId",
    "$Reparse",
)  # Only in root directory


def _extract_root_name(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


PlatformType = Union[str, Platform, None]


def normalize_platform(name: PlatformType) -> Platform:
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


class FileSanitizer(NameSanitizer):
    _INVALID_PATH_CHARS = "".join(unprintable_ascii_chars)
    _INVALID_FILENAME_CHARS = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS = _INVALID_PATH_CHARS + ':*?"<>|\t\n\r\x0b\x0c'
    _INVALID_WIN_FILENAME_CHARS = _INVALID_FILENAME_CHARS + _INVALID_WIN_PATH_CHARS + "\\"

    _ERROR_MSG_TEMPLATE = "invalid char found: invalids=({invalid}), value={value}"

    @property
    def platform(self) -> Platform:
        return self.__platform

    @property
    def reserved_keywords(self) -> Tuple[str, ...]:
        return (".", "..")

    @property
    def min_len(self) -> int:
        return self._min_len

    @property
    def max_len(self) -> int:
        return self._max_len

    def __init__(
        self, min_len: Optional[int], max_len: Optional[int], platform: PlatformType = None
    ) -> None:
        self.__platform = normalize_platform(platform)

        if min_len is None:
            min_len = 1
        self._min_len = max(min_len, 1)

        if max_len in [None, -1]:
            self._max_len = self._get_default_max_path_len()
        else:
            self._max_len = cast(int, max_len)

    def _is_universal(self) -> bool:
        return self.platform == Platform.UNIVERSAL

    def _is_linux(self) -> bool:
        return self.platform == Platform.LINUX

    def _is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    def _is_macos(self) -> bool:
        return self.platform == Platform.MACOS

    def _validate_max_len(self) -> None:
        if self.max_len < 1:
            raise ValueError("max_len must be greater or equals to one")

        if self.min_len > self.max_len:
            raise ValueError("min_len must be lower than max_len")

    def _validate_reserved_keywords(self, name: str) -> None:
        root_name = _extract_root_name(name)
        if self._is_reserved_keyword(root_name.upper()):
            raise ReservedNameError(
                "'{}' is a reserved name".format(root_name),
                reusable_name=False,
                reserved_name=root_name,
                platform=self.platform,
            )

    def _get_default_max_path_len(self) -> int:
        if self._is_linux():
            return 4096

        if self._is_windows():
            return 260

        if self._is_macos():
            return 1024

        return 260  # universal

    @staticmethod
    def _findall_to_str(match: List[Any]) -> str:
        return ", ".join([repr(text) for text in match])


class FileNameSanitizer(FileSanitizer):

    __WINDOWS_RESERVED_FILE_NAMES = ("CON", "PRN", "AUX", "CLOCK$", "NUL") + tuple(
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
    def reserved_keywords(self) -> Tuple[str, ...]:
        common_keywords = super(FileNameSanitizer, self).reserved_keywords

        if self._is_universal() or self._is_windows():
            return common_keywords + self.__WINDOWS_RESERVED_FILE_NAMES

        return common_keywords

    def __init__(
        self,
        min_len: Optional[int] = 1,
        max_len: Optional[int] = _DEFAULT_MAX_FILENAME_LEN,
        platform: PlatformType = None,
    ) -> None:
        super(FileNameSanitizer, self).__init__(
            min_len=min_len,
            max_len=(
                cast(int, max_len) if max_len not in [None, -1] else _DEFAULT_MAX_FILENAME_LEN
            ),
            platform=platform,
        )

        self._max_len = min(self._max_len, self._get_default_max_path_len())
        self._validate_max_len()
        self._sanitize_regexp = self._get_sanitize_regexp()

    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:
        self._validate_null_string(value)

        sanitized_filename = self._sanitize_regexp.sub(replacement_text, str(value))
        sanitized_filename = sanitized_filename[: self.max_len]

        try:
            self.validate(sanitized_filename)
        except ReservedNameError as e:
            if e.reusable_name is False:
                sanitized_filename = re.sub(
                    re.escape(e.reserved_name), "{}_".format(e.reserved_name), sanitized_filename
                )
        except InvalidCharError:
            if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
                sanitized_filename = sanitized_filename.rstrip(" .")

        if is_pathlike_obj(value):
            return Path(sanitized_filename)

        return sanitized_filename

    def validate(self, value: PathType) -> None:
        self._validate_null_string(value)

        unicode_filename = preprocess(value)
        value_len = len(unicode_filename)

        if value_len > self.max_len:
            raise InvalidLengthError(
                "filename is too long: expected<={:d}, actual={:d}".format(self.max_len, value_len)
            )
        if value_len < self.min_len:
            raise InvalidLengthError(
                "filename is too short: expected>={:d}, actual={:d}".format(self.min_len, value_len)
            )

        self._validate_reserved_keywords(unicode_filename)

        if self._is_universal() or self._is_windows():
            self.__validate_win_filename(unicode_filename)
        else:
            self.__validate_unix_filename(unicode_filename)

    def __validate_unix_filename(self, unicode_filename: str) -> None:
        match = self.__RE_INVALID_FILENAME.findall(unicode_filename)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_filename)
                )
            )

    def __validate_win_filename(self, unicode_filename: str) -> None:
        match = self.__RE_INVALID_WIN_FILENAME.findall(unicode_filename)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_filename)
                ),
                platform=Platform.WINDOWS,
            )

        if unicode_filename[-1] in (" ", "."):
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=re.escape(unicode_filename[-1]), value=repr(unicode_filename)
                ),
                platform=Platform.WINDOWS,
                description="Do not end a file or directory name with a space or a period",
            )

    def _get_sanitize_regexp(self) -> Pattern:
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
    __RE_NTFS_RESERVED = re.compile(
        "|".join("^/{}$".format(re.escape(pattern)) for pattern in _NTFS_RESERVED_FILE_NAMES),
        re.IGNORECASE,
    )

    def __init__(
        self,
        min_len: Optional[int] = 1,
        max_len: Optional[int] = None,
        platform: PlatformType = None,
    ) -> None:
        super(FilePathSanitizer, self).__init__(
            min_len=min_len, max_len=max_len, platform=platform,
        )

        self._max_len = min(self._max_len, self._get_default_max_path_len())

        self._validate_max_len()

        self._sanitize_regexp = self._get_sanitize_regexp()
        self.__fname_sanitizer = FileNameSanitizer(
            min_len=min_len, max_len=max_len, platform=platform
        )

        if self._is_universal() or self._is_windows():
            self.__split_drive = ntpath.splitdrive
        else:
            self.__split_drive = posixpath.splitdrive

    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:
        self._validate_null_string(value)

        unicode_file_path = preprocess(value)
        drive, unicode_file_path = self.__split_drive(unicode_file_path)
        sanitized_path = self._sanitize_regexp.sub(replacement_text, unicode_file_path)
        if self._is_windows():
            path_separator = "\\"
        else:
            path_separator = "/"

        sanitized_entries = []  # type: List[str]
        if drive:
            sanitized_entries.append(drive)
        for entry in sanitized_path.replace("\\", "/").split("/"):
            if entry in _NTFS_RESERVED_FILE_NAMES:
                sanitized_entries.append("{}_".format(entry))
                continue

            try:
                sanitized_entries.append(str(self.__fname_sanitizer.sanitize(entry)))
            except ValidationError as e:
                if e.reason == ErrorReason.NULL_NAME:
                    if not sanitized_entries:
                        sanitized_entries.append("")
                else:
                    raise
        sanitized_path = path_separator.join(sanitized_entries)

        if is_pathlike_obj(value):
            return Path(sanitized_path)

        return sanitized_path

    def validate(self, value: PathType) -> None:
        self._validate_null_string(value)

        _drive, value = self.__split_drive(str(value))
        if not value:
            return

        file_path = os.path.normpath(value)
        unicode_file_path = preprocess(file_path)
        value_len = len(unicode_file_path)

        if value_len > self.max_len:
            raise InvalidLengthError(
                "file path is too long: expected<={:d}, actual={:d}".format(self.max_len, value_len)
            )
        if value_len < self.min_len:
            raise InvalidLengthError(
                "file path is too short: expected>={:d}, actual={:d}".format(
                    self.min_len, value_len
                )
            )

        self._validate_reserved_keywords(unicode_file_path)
        unicode_file_path = unicode_file_path.replace("\\", "/")
        for entry in unicode_file_path.split("/"):
            if not entry:
                continue

            self.__fname_sanitizer._validate_reserved_keywords(entry)

        if self._is_universal() or self._is_windows():
            self.__validate_win_file_path(unicode_file_path)
        else:
            self.__validate_unix_file_path(unicode_file_path)

    def __validate_unix_file_path(self, unicode_file_path: str) -> None:
        match = self.__RE_INVALID_PATH.findall(unicode_file_path)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_file_path)
                )
            )

    def __validate_win_file_path(self, unicode_file_path: str) -> None:
        match = self.__RE_INVALID_WIN_PATH.findall(unicode_file_path)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_file_path)
                ),
                platform=Platform.WINDOWS,
            )

        _drive, value = self.__split_drive(unicode_file_path)
        if value:
            match_reserved = self.__RE_NTFS_RESERVED.search(value)
            if match_reserved:
                reserved_name = match_reserved.group()
                raise ReservedNameError(
                    "'{}' is a reserved name".format(reserved_name),
                    reusable_name=False,
                    reserved_name=reserved_name,
                    platform=self.platform,
                )

    def _get_sanitize_regexp(self) -> Pattern:
        if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
            return self.__RE_INVALID_WIN_PATH

        return self.__RE_INVALID_PATH


def validate_filename(
    filename: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: int = _DEFAULT_MAX_FILENAME_LEN,
) -> None:
    """Verifying whether the ``filename`` is a valid file name or not.

    Args:
        filename:
            Filename to validate.
        platform:
            .. include:: platform.txt
        min_len:
            Minimum length of the ``filename``. The value must be greater or equal to one.
            Defaults to ``1``.
        max_len:
            Maximum length the ``filename``. The value must be lower than:

                - ``Linux``: 4096
                - ``macOS``: 1024
                - ``Windows``: 260
                - ``Universal``: 260

            Defaults to ``255``.

    Raises:
        InvalidLengthError:
            If the ``filename`` is longer than ``max_len`` characters.
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
        `Naming Files, Paths, and Namespaces - Win32 apps | Microsoft Docs
        <https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file>`__
    """

    FileNameSanitizer(platform=platform, min_len=min_len, max_len=max_len).validate(filename)


def validate_filepath(
    file_path: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: Optional[int] = None,
) -> None:
    """Verifying whether the ``file_path`` is a valid file path or not.

    Args:
        file_path:
            File path to validate.
        platform:
            .. include:: platform.txt
        min_len:
            Minimum length of the ``file_path``. The value must be greater or equal to one.
            Defaults to ``1``.
        max_len:
            Maximum length of the ``file_path`` length. If the value is |None|,
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
            If the ``file_path`` is longer than ``max_len`` characters.

    Example:
        :ref:`example-validate-file-path`

    See Also:
        `Naming Files, Paths, and Namespaces - Win32 apps | Microsoft Docs
        <https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file>`__
    """

    FilePathSanitizer(platform=platform, min_len=min_len, max_len=max_len).validate(file_path)


def validate_file_path(file_path, platform=None, max_path_len=None):
    # Deprecated
    validate_filepath(file_path, platform, max_path_len)


def is_valid_filename(
    filename: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: Optional[int] = None,
) -> bool:
    return FileNameSanitizer(platform=platform, min_len=min_len, max_len=max_len).is_valid(filename)


def is_valid_filepath(
    file_path: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: Optional[int] = None,
) -> bool:
    return FilePathSanitizer(platform=platform, min_len=min_len, max_len=max_len).is_valid(
        file_path
    )


def sanitize_filename(
    filename: PathType,
    replacement_text: str = "",
    platform: Optional[str] = None,
    max_len: Optional[int] = _DEFAULT_MAX_FILENAME_LEN,
) -> PathType:
    """Make a valid filename from a string.

    To make a valid filename the function does:

        - Replace invalid characters as file names included in the ``filename``
          with the ``replacement_text``. Invalid characters are:

            - unprintable characters
            - |invalid_filename_chars|
            - for Windows only: |invalid_win_filename_chars|

        - Append underscore (``"_"``) at the tail of the name if sanitized name
          is one of the reserved names by the operating system.

    Args:
        filename: Filename to sanitize.
        replacement_text:
            Replacement text for invalid characters. Defaults to ``""``.
        platform:
            .. include:: platform.txt
        max_len:
            The upper limit of the ``filename`` length. Truncate the name length if
            the ``filename`` length exceeds this value.
            Defaults to ``255``.

    Returns:
        Same type as the ``filename`` (str or PathLike object):
            Sanitized filename.

    Raises:
        ValueError:
            If the ``filename`` is an invalid filename.

    Example:
        :ref:`example-sanitize-filename`
    """

    return FileNameSanitizer(platform=platform, max_len=max_len).sanitize(
        filename, replacement_text
    )


def sanitize_filepath(
    file_path: PathType,
    replacement_text: str = "",
    platform: Optional[str] = None,
    max_len: Optional[int] = None,
) -> PathType:
    """Make a valid file path from a string.

    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``.
    Invalid characters are as followings:
    |invalid_file_path_chars|, |invalid_win_file_path_chars| (and non printable characters).

    Args:
        file_path:
            File path to sanitize.
        replacement_text:
            Replacement text for invalid characters.
            Defaults to ``""``.
        platform:
            .. include:: platform.txt
        max_len:
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

    return FilePathSanitizer(platform=platform, max_len=max_len).sanitize(
        file_path, replacement_text
    )


def sanitize_file_path(file_path, replacement_text="", platform=None, max_path_len=None):
    # Deprecated
    return sanitize_filepath(file_path, platform, max_path_len)
