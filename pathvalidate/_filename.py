"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import itertools
import ntpath
import posixpath
import re
from pathlib import Path
from typing import Optional, Pattern, Tuple

from ._base import AbstractSanitizer, BaseFile, BaseValidator
from ._common import PathType, PlatformType, findall_to_str, to_str, validate_pathtype
from ._const import DEFAULT_MIN_LEN, INVALID_CHAR_ERR_MSG_TMPL, Platform
from .error import ErrorReason, InvalidCharError, InvalidLengthError, ValidationError
from .handler import NullValueHandler


_DEFAULT_MAX_FILENAME_LEN = 255
_RE_INVALID_FILENAME = re.compile(f"[{re.escape(BaseFile._INVALID_FILENAME_CHARS):s}]", re.UNICODE)
_RE_INVALID_WIN_FILENAME = re.compile(
    f"[{re.escape(BaseFile._INVALID_WIN_FILENAME_CHARS):s}]", re.UNICODE
)


class FileNameSanitizer(AbstractSanitizer):
    def __init__(
        self,
        min_len: int = DEFAULT_MIN_LEN,
        max_len: int = _DEFAULT_MAX_FILENAME_LEN,
        platform: Optional[PlatformType] = None,
        check_reserved: bool = True,
        null_value_handler: Optional[NullValueHandler] = None,
    ) -> None:
        super().__init__(
            min_len=min_len,
            max_len=max_len,
            check_reserved=check_reserved,
            null_value_handler=null_value_handler,
            platform_max_len=_DEFAULT_MAX_FILENAME_LEN,
            platform=platform,
        )

        self._sanitize_regexp = self._get_sanitize_regexp()
        self.__validator = FileNameValidator(
            min_len=self.min_len,
            max_len=self.max_len,
            check_reserved=check_reserved,
            platform=self.platform,
        )

    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:
        try:
            validate_pathtype(value, allow_whitespaces=not self._is_windows(include_universal=True))
        except ValidationError as e:
            if e.reason == ErrorReason.NULL_NAME:
                if isinstance(value, Path):
                    raise

                return self._null_value_handler(e)
            raise

        sanitized_filename = self._sanitize_regexp.sub(replacement_text, str(value))
        sanitized_filename = sanitized_filename[: self.max_len]

        try:
            self.__validator.validate(sanitized_filename)
        except ValidationError as e:
            if e.reason == ErrorReason.RESERVED_NAME and e.reusable_name is False:
                sanitized_filename = re.sub(
                    re.escape(e.reserved_name), f"{e.reserved_name}_", sanitized_filename
                )
            elif e.reason == ErrorReason.INVALID_CHARACTER and self._is_windows(
                include_universal=True
            ):
                # Do not start a file or directory name with a space
                sanitized_filename = sanitized_filename.lstrip(" ")

                # Do not end a file or directory name with a space or a period
                sanitized_filename = sanitized_filename.rstrip(" ")
                if sanitized_filename not in (".", ".."):
                    sanitized_filename = sanitized_filename.rstrip(" .")
            elif e.reason == ErrorReason.NULL_NAME:
                sanitized_filename = self._null_value_handler(e)
            else:
                raise

        if isinstance(value, Path):
            return Path(sanitized_filename)

        return sanitized_filename

    def _get_sanitize_regexp(self) -> Pattern[str]:
        if self._is_windows(include_universal=True):
            return _RE_INVALID_WIN_FILENAME

        return _RE_INVALID_FILENAME


class FileNameValidator(BaseValidator):
    _WINDOWS_RESERVED_FILE_NAMES = ("CON", "PRN", "AUX", "CLOCK$", "NUL") + tuple(
        f"{name:s}{num:d}" for name, num in itertools.product(("COM", "LPT"), range(1, 10))
    )
    _MACOS_RESERVED_FILE_NAMES = (":",)

    @property
    def reserved_keywords(self) -> Tuple[str, ...]:
        common_keywords = super().reserved_keywords

        if self._is_universal():
            return (
                common_keywords
                + self._WINDOWS_RESERVED_FILE_NAMES
                + self._MACOS_RESERVED_FILE_NAMES
            )

        if self._is_windows():
            return common_keywords + self._WINDOWS_RESERVED_FILE_NAMES

        if self._is_posix() or self._is_macos():
            return common_keywords + self._MACOS_RESERVED_FILE_NAMES

        return common_keywords

    def __init__(
        self,
        min_len: int = DEFAULT_MIN_LEN,
        max_len: int = _DEFAULT_MAX_FILENAME_LEN,
        platform: Optional[PlatformType] = None,
        check_reserved: bool = True,
    ) -> None:
        super().__init__(
            min_len=min_len,
            max_len=max_len,
            check_reserved=check_reserved,
            platform_max_len=_DEFAULT_MAX_FILENAME_LEN,
            platform=platform,
        )

    def validate(self, value: PathType) -> None:
        validate_pathtype(value, allow_whitespaces=not self._is_windows(include_universal=True))

        unicode_filename = to_str(value)
        value_len = len(unicode_filename)

        self.validate_abspath(unicode_filename)

        if value_len > self.max_len:
            raise InvalidLengthError(
                f"filename is too long: expected<={self.max_len:d}, actual={value_len:d}"
            )
        if value_len < self.min_len:
            raise InvalidLengthError(
                f"filename is too short: expected>={self.min_len:d}, actual={value_len:d}"
            )

        self._validate_reserved_keywords(unicode_filename)

        if self._is_windows(include_universal=True):
            self.__validate_win_filename(unicode_filename)
        else:
            self.__validate_unix_filename(unicode_filename)

    def validate_abspath(self, value: str) -> None:
        err = ValidationError(
            description=f"found an absolute path ({value}), expected a filename",
            platform=self.platform,
            reason=ErrorReason.FOUND_ABS_PATH,
        )

        if self._is_windows(include_universal=True):
            if ntpath.isabs(value):
                raise err

        if posixpath.isabs(value):
            raise err

    def __validate_unix_filename(self, unicode_filename: str) -> None:
        match = _RE_INVALID_FILENAME.findall(unicode_filename)
        if match:
            raise InvalidCharError(
                INVALID_CHAR_ERR_MSG_TMPL.format(
                    invalid=findall_to_str(match), value=repr(unicode_filename)
                )
            )

    def __validate_win_filename(self, unicode_filename: str) -> None:
        match = _RE_INVALID_WIN_FILENAME.findall(unicode_filename)
        if match:
            raise InvalidCharError(
                INVALID_CHAR_ERR_MSG_TMPL.format(
                    invalid=findall_to_str(match), value=repr(unicode_filename)
                ),
                platform=Platform.WINDOWS,
            )

        if unicode_filename in (".", ".."):
            return

        KB2829981_err_tmpl = "{}. Refer: https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/file-folder-name-whitespace-characters"  # noqa: E501

        if unicode_filename[-1] in (" ", "."):
            raise InvalidCharError(
                INVALID_CHAR_ERR_MSG_TMPL.format(
                    invalid=re.escape(unicode_filename[-1]), value=repr(unicode_filename)
                ),
                platform=Platform.WINDOWS,
                description=KB2829981_err_tmpl.format(
                    "Do not end a file or directory name with a space or a period"
                ),
            )

        if unicode_filename[0] in (" "):
            raise InvalidCharError(
                INVALID_CHAR_ERR_MSG_TMPL.format(
                    invalid=re.escape(unicode_filename[0]), value=repr(unicode_filename)
                ),
                platform=Platform.WINDOWS,
                description=KB2829981_err_tmpl.format(
                    "Do not start a file or directory name with a space"
                ),
            )


def validate_filename(
    filename: PathType,
    platform: Optional[PlatformType] = None,
    min_len: int = DEFAULT_MIN_LEN,
    max_len: int = _DEFAULT_MAX_FILENAME_LEN,
    check_reserved: bool = True,
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
            Maximum length of the ``filename``. The value must be lower than:

                - ``Linux``: 4096
                - ``macOS``: 1024
                - ``Windows``: 260
                - ``universal``: 260

            Defaults to ``255``.
        check_reserved:
            If |True|, check reserved names of the ``platform``.

    Raises:
        ValidationError (ErrorReason.INVALID_LENGTH):
            If the ``filename`` is longer than ``max_len`` characters.
        ValidationError (ErrorReason.INVALID_CHARACTER):
            If the ``filename`` includes invalid character(s) for a filename:
            |invalid_filename_chars|.
            The following characters are also invalid for Windows platforms:
            |invalid_win_filename_chars|.
        ValidationError (ErrorReason.RESERVED_NAME):
            If the ``filename`` equals reserved name by OS.
            Windows reserved name is as follows:
            ``"CON"``, ``"PRN"``, ``"AUX"``, ``"NUL"``, ``"COM[1-9]"``, ``"LPT[1-9]"``.

    Example:
        :ref:`example-validate-filename`

    See Also:
        `Naming Files, Paths, and Namespaces - Win32 apps | Microsoft Docs
        <https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file>`__
    """

    FileNameValidator(
        platform=platform, min_len=min_len, max_len=max_len, check_reserved=check_reserved
    ).validate(filename)


def is_valid_filename(
    filename: PathType,
    platform: Optional[PlatformType] = None,
    min_len: int = DEFAULT_MIN_LEN,
    max_len: Optional[int] = None,
    check_reserved: bool = True,
) -> bool:
    """Check whether the ``filename`` is a valid name or not.

    Args:
        filename:
            A filename to be checked.

    Example:
        :ref:`example-is-valid-filename`

    See Also:
        :py:func:`.validate_filename()`
    """

    return FileNameValidator(
        platform=platform,
        min_len=min_len,
        max_len=-1 if max_len is None else max_len,
        check_reserved=check_reserved,
    ).is_valid(filename)


def sanitize_filename(
    filename: PathType,
    replacement_text: str = "",
    platform: Optional[PlatformType] = None,
    max_len: Optional[int] = _DEFAULT_MAX_FILENAME_LEN,
    check_reserved: bool = True,
    null_value_handler: Optional[NullValueHandler] = None,
) -> PathType:
    """Make a valid filename from a string.

    To make a valid filename, the function does the following:

        - Replace invalid characters as file names included in the ``filename``
          with the ``replacement_text``. Invalid characters are:

            - unprintable characters
            - |invalid_filename_chars|
            - for Windows (or universal) only: |invalid_win_filename_chars|

        - Append underscore (``"_"``) at the tail of the return value if a sanitized name
          is one of the reserved names by operating systems
          (only when ``check_reserved`` is |True|).

    Args:
        filename: Filename to sanitize.
        replacement_text:
            Replacement text for invalid characters. Defaults to ``""``.
        platform:
            Target platform name of the filename.

            .. include:: platform.txt
        max_len:
            Maximum length of the ``filename`` length. Truncate the name length if
            the ``filename`` length exceeds this value.
            Defaults to ``255``.
        check_reserved:
            If |True|, sanitize reserved names of the ``platform``.
        null_value_handler:
            Function called when a value after sanitization is an empty string.
            Defaults to ``pathvalidate.handler.return_null_string()`` that just return ``""``.

    Returns:
        Same type as the ``filename`` (str or PathLike object):
            Sanitized filename.

    Raises:
        ValueError:
            If the ``filename`` is an invalid filename.

    Example:
        :ref:`example-sanitize-filename`
    """

    return FileNameSanitizer(
        platform=platform,
        max_len=-1 if max_len is None else max_len,
        check_reserved=check_reserved,
        null_value_handler=null_value_handler,
    ).sanitize(filename, replacement_text)
