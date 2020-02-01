"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import ntpath
import os.path
import posixpath
import re
from pathlib import Path
from typing import List, Optional, Pattern, Tuple, cast

from ._common import (
    PathType,
    Platform,
    PlatformType,
    is_pathlike_obj,
    preprocess,
    unprintable_ascii_chars,
    validate_pathtype,
)
from ._const import _NTFS_RESERVED_FILE_NAMES
from ._interface import AbstractSanitizer, AbstractValidator
from .error import (
    ErrorReason,
    InvalidCharError,
    InvalidLengthError,
    ReservedNameError,
    ValidationError,
)


_DEFAULT_MAX_FILENAME_LEN = 255


def _extract_root_name(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


class BaseValidator(AbstractValidator):
    def _validate_reserved_keywords(self, name: str) -> None:
        root_name = _extract_root_name(name)
        if self._is_reserved_keyword(root_name.upper()):
            raise ReservedNameError(
                "'{}' is a reserved name".format(root_name),
                reusable_name=False,
                reserved_name=root_name,
                platform=self.platform,
            )


class FileNameSanitizer(AbstractSanitizer):
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
        self.__validator = FileNameValidator(
            min_len=self.min_len, max_len=self.max_len, platform=self.platform
        )

    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:
        try:
            validate_pathtype(value)
        except ValidationError as e:
            if e.reason == ErrorReason.NULL_NAME:
                return ""
            raise

        sanitized_filename = self._sanitize_regexp.sub(replacement_text, str(value))
        sanitized_filename = sanitized_filename[: self.max_len]

        try:
            self.__validator.validate(sanitized_filename)
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

    def _get_sanitize_regexp(self) -> Pattern:
        if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
            return self._RE_INVALID_WIN_FILENAME

        return self._RE_INVALID_FILENAME


class FileNameValidator(BaseValidator):
    @property
    def reserved_keywords(self) -> Tuple[str, ...]:
        common_keywords = super(FileNameValidator, self).reserved_keywords

        if self._is_universal() or self._is_windows():
            return common_keywords + self._WINDOWS_RESERVED_FILE_NAMES

        return common_keywords

    def __init__(
        self,
        min_len: Optional[int] = 1,
        max_len: Optional[int] = _DEFAULT_MAX_FILENAME_LEN,
        platform: PlatformType = None,
    ) -> None:
        super(FileNameValidator, self).__init__(
            min_len=min_len,
            max_len=(
                cast(int, max_len) if max_len not in [None, -1] else _DEFAULT_MAX_FILENAME_LEN
            ),
            platform=platform,
        )

        self._max_len = min(self._max_len, self._get_default_max_path_len())
        self._validate_max_len()

    def validate(self, value: PathType) -> None:
        validate_pathtype(value)

        unicode_filename = preprocess(value)
        value_len = len(unicode_filename)

        self.validate_abspath(unicode_filename)

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

    def validate_abspath(self, value: str) -> None:
        if any([ntpath.isabs(value), posixpath.isabs(value)]):
            raise ValidationError(
                description="found an absolute path ({}), expected a filename".format(value),
                platform=self.platform,
                reason=ErrorReason.FOUND_ABS_PATH,
            )

    def __validate_unix_filename(self, unicode_filename: str) -> None:
        match = self._RE_INVALID_FILENAME.findall(unicode_filename)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_filename)
                )
            )

    def __validate_win_filename(self, unicode_filename: str) -> None:
        match = self._RE_INVALID_WIN_FILENAME.findall(unicode_filename)
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


class FilePathSanitizer(AbstractSanitizer):
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
        self.__fpath_validator = FilePathValidator(
            min_len=self.min_len, max_len=self.max_len, platform=self.platform
        )
        self.__fname_sanitizer = FileNameSanitizer(
            min_len=self.min_len, max_len=self.max_len, platform=self.platform
        )

        if self._is_universal() or self._is_windows():
            self.__split_drive = ntpath.splitdrive
        else:
            self.__split_drive = posixpath.splitdrive

    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:
        if not value:
            return ""

        self.__fpath_validator.validate_abspath(value)

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

            sanitized_entry = str(self.__fname_sanitizer.sanitize(entry))
            if not sanitized_entry:
                if not sanitized_entries:
                    sanitized_entries.append("")
                continue

            sanitized_entries.append(sanitized_entry)

        sanitized_path = path_separator.join(sanitized_entries)

        if is_pathlike_obj(value):
            return Path(sanitized_path)

        return sanitized_path

    def _get_sanitize_regexp(self) -> Pattern:
        if self.platform in [Platform.UNIVERSAL, Platform.WINDOWS]:
            return self._RE_INVALID_WIN_PATH

        return self._RE_INVALID_PATH


class FilePathValidator(BaseValidator):
    @property
    def reserved_keywords(self) -> Tuple[str, ...]:
        common_keywords = super(FilePathValidator, self).reserved_keywords

        if any([self._is_universal(), self._is_linux(), self._is_macos()]):
            return common_keywords + ("/",)

        return common_keywords

    def __init__(
        self,
        min_len: Optional[int] = 1,
        max_len: Optional[int] = None,
        platform: PlatformType = None,
    ) -> None:
        super(FilePathValidator, self).__init__(
            min_len=min_len, max_len=max_len, platform=platform,
        )

        self._max_len = min(self._max_len, self._get_default_max_path_len())
        self._validate_max_len()

        self.__fname_validator = FileNameValidator(
            min_len=min_len, max_len=max_len, platform=platform
        )

        if self._is_universal() or self._is_windows():
            self.__split_drive = ntpath.splitdrive
        else:
            self.__split_drive = posixpath.splitdrive

    def validate(self, value: PathType) -> None:
        validate_pathtype(value)
        self.validate_abspath(value)

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

            self.__fname_validator._validate_reserved_keywords(entry)

        if self._is_universal() or self._is_windows():
            self.__validate_win_file_path(unicode_file_path)
        else:
            self.__validate_unix_file_path(unicode_file_path)

    def validate_abspath(self, value: PathType) -> None:
        value = str(value)
        is_posix_abs = posixpath.isabs(value)
        is_nt_abs = ntpath.isabs(value)
        err_object = ValidationError(
            description=(
                "an invalid absolute file path ({}) for the platform ({}).".format(
                    value, self.platform.value
                )
                + " specify an appropriate platform or 'auto'."
            ),
            platform=self.platform,
            reason=ErrorReason.MALFORMED_ABS_PATH,
        )

        if self._is_universal() and any([is_posix_abs, is_nt_abs]):
            raise err_object

        if any([self._is_windows(), self._is_universal()]) and posixpath.isabs(value):
            raise err_object

        drive, _tail = ntpath.splitdrive(value)
        if not self._is_windows() and drive and ntpath.isabs(value):
            raise err_object

    def __validate_unix_file_path(self, unicode_file_path: str) -> None:
        match = self._RE_INVALID_PATH.findall(unicode_file_path)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_file_path)
                )
            )

    def __validate_win_file_path(self, unicode_file_path: str) -> None:
        match = self._RE_INVALID_WIN_PATH.findall(unicode_file_path)
        if match:
            raise InvalidCharError(
                self._ERROR_MSG_TEMPLATE.format(
                    invalid=self._findall_to_str(match), value=repr(unicode_file_path)
                ),
                platform=Platform.WINDOWS,
            )

        _drive, value = self.__split_drive(unicode_file_path)
        if value:
            match_reserved = self._RE_NTFS_RESERVED.search(value)
            if match_reserved:
                reserved_name = match_reserved.group()
                raise ReservedNameError(
                    "'{}' is a reserved name".format(reserved_name),
                    reusable_name=False,
                    reserved_name=reserved_name,
                    platform=self.platform,
                )


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
            Target platform name of the filename.

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

    FileNameValidator(platform=platform, min_len=min_len, max_len=max_len).validate(filename)


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
            Target platform name of the file path.

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
        InvalidCharError:
            If the ``file_path`` includes invalid char(s):
            |invalid_file_path_chars|.
            The following characters are also invalid for Windows platform:
            |invalid_win_file_path_chars|
        InvalidLengthError:
            If the ``file_path`` is longer than ``max_len`` characters.
        ValidationError:
            If ``file_path`` include invalid values.

    Example:
        :ref:`example-validate-file-path`

    See Also:
        `Naming Files, Paths, and Namespaces - Win32 apps | Microsoft Docs
        <https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file>`__
    """

    FilePathValidator(platform=platform, min_len=min_len, max_len=max_len).validate(file_path)


def validate_file_path(file_path, platform=None, max_path_len=None):
    # Deprecated
    validate_filepath(file_path, platform, max_path_len)


def is_valid_filename(
    filename: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: Optional[int] = None,
) -> bool:
    return FileNameValidator(platform=platform, min_len=min_len, max_len=max_len).is_valid(filename)


def is_valid_filepath(
    file_path: PathType,
    platform: Optional[str] = None,
    min_len: int = 1,
    max_len: Optional[int] = None,
) -> bool:
    return FilePathValidator(platform=platform, min_len=min_len, max_len=max_len).is_valid(
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
            Target platform name of the filename.

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
            Target platform name of the file path.

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
