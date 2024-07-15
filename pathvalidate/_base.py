"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
import os
import sys
import warnings
from typing import ClassVar, Optional, Sequence, Tuple

from ._common import normalize_platform, unprintable_ascii_chars
from ._const import DEFAULT_MIN_LEN, Platform
from ._types import PathType, PlatformType
from .error import ReservedNameError, ValidationError
from .handler import NullValueHandler, ReservedNameHandler, ValidationErrorHandler


class BaseFile:
    _INVALID_PATH_CHARS: ClassVar[str] = "".join(unprintable_ascii_chars)
    _INVALID_FILENAME_CHARS: ClassVar[str] = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS: ClassVar[str] = _INVALID_PATH_CHARS + ':*?"<>|\t\n\r\x0b\x0c'
    _INVALID_WIN_FILENAME_CHARS: ClassVar[str] = (
        _INVALID_FILENAME_CHARS + _INVALID_WIN_PATH_CHARS + "\\"
    )
    _DEFAULT_MAX_FILENAME_LEN = 255

    @property
    def platform(self) -> Platform:
        return self.__platform

    @property
    def reserved_keywords(self) -> Tuple[str, ...]:
        return self._additional_reserved_names

    @property
    def max_len(self) -> int:
        warnings.warn(
            "'max_len' is deprecated. Use 'max_filepath_len' instead.",
            DeprecationWarning,
        )
        return self._max_filepath_len

    @property
    def max_filename_len(self) -> int:
        return self._max_filename_len

    @property
    def max_filepath_len(self) -> int:
        return self._max_filepath_len

    def __init__(
        self,
        fs_encoding: Optional[str],
        max_filename_len: Optional[int] = None,
        max_filepath_len: Optional[int] = None,
        additional_reserved_names: Optional[Sequence[str]] = None,
        platform_max_filename_len: Optional[int] = None,
        platform_max_filepath_len: Optional[int] = None,
        platform: Optional[PlatformType] = None,
    ) -> None:
        if additional_reserved_names is None:
            additional_reserved_names = tuple()
        self._additional_reserved_names = tuple(n.upper() for n in additional_reserved_names)

        self.__platform = normalize_platform(platform)

        # determine max filepath length
        if platform_max_filepath_len is None:
            platform_max_filepath_len = self._get_default_max_path_len()

        if max_filepath_len is None or max_filepath_len <= 0:
            self._max_filepath_len = platform_max_filepath_len
        else:
            self._max_filepath_len = min(max_filepath_len, platform_max_filepath_len)

        # determine max filename length
        if platform_max_filename_len is None:
            platform_max_filename_len = self._get_default_max_name_len()

        if max_filename_len is None or max_filename_len <= 0:
            self._max_filename_len = platform_max_filename_len
        else:
            self._max_filename_len = max_filename_len
        # name cannot be longer than max path length
        self._max_filename_len = min(self._max_filename_len, self._max_filepath_len)

        if fs_encoding:
            self._fs_encoding = fs_encoding
        else:
            self._fs_encoding = sys.getfilesystemencoding()

    def _is_posix(self) -> bool:
        return self.platform == Platform.POSIX

    def _is_universal(self) -> bool:
        return self.platform == Platform.UNIVERSAL

    def _is_linux(self, include_universal: bool = False) -> bool:
        if include_universal:
            return self.platform in (Platform.UNIVERSAL, Platform.LINUX)

        return self.platform == Platform.LINUX

    def _is_windows(self, include_universal: bool = False) -> bool:
        if include_universal:
            return self.platform in (Platform.UNIVERSAL, Platform.WINDOWS)

        return self.platform == Platform.WINDOWS

    def _is_macos(self, include_universal: bool = False) -> bool:
        if include_universal:
            return self.platform in (Platform.UNIVERSAL, Platform.MACOS)

        return self.platform == Platform.MACOS

    def _get_default_max_path_len(self) -> int:
        if self._is_linux():
            return 4096

        if self._is_windows():
            return 260

        if self._is_posix() or self._is_macos():
            return 1024

        return 260  # universal

    def _get_default_max_name_len(self) -> int:
        return self._DEFAULT_MAX_FILENAME_LEN


class AbstractValidator(BaseFile, metaclass=abc.ABCMeta):
    def __init__(
        self,
        fs_encoding: Optional[str],
        check_reserved: bool,
        max_filename_len: Optional[int] = None,
        max_filepath_len: Optional[int] = None,
        additional_reserved_names: Optional[Sequence[str]] = None,
        platform_max_filepath_len: Optional[int] = None,
        platform: Optional[PlatformType] = None,
    ) -> None:
        self._check_reserved = check_reserved

        super().__init__(
            fs_encoding,
            max_filename_len=max_filename_len,
            max_filepath_len=max_filepath_len,
            additional_reserved_names=additional_reserved_names,
            platform_max_filepath_len=platform_max_filepath_len,
            platform=platform,
        )

    @property
    @abc.abstractmethod
    def min_len(self) -> int:  # pragma: no cover
        pass

    @abc.abstractmethod
    def validate(self, value: PathType) -> None:  # pragma: no cover
        pass

    def is_valid(self, value: PathType) -> bool:
        try:
            self.validate(value)
        except (TypeError, ValidationError):
            return False

        return True

    def _is_reserved_keyword(self, value: str) -> bool:
        return value in self.reserved_keywords


class AbstractSanitizer(BaseFile, metaclass=abc.ABCMeta):
    def __init__(
        self,
        validator: AbstractValidator,
        fs_encoding: Optional[str],
        validate_after_sanitize: bool,
        max_filename_len: Optional[int] = None,
        max_filepath_len: Optional[int] = None,
        null_value_handler: Optional[ValidationErrorHandler] = None,
        reserved_name_handler: Optional[ValidationErrorHandler] = None,
        additional_reserved_names: Optional[Sequence[str]] = None,
        platform_max_filepath_len: Optional[int] = None,
        platform: Optional[PlatformType] = None,
    ) -> None:
        super().__init__(
            fs_encoding=fs_encoding,
            additional_reserved_names=additional_reserved_names,
            platform_max_filepath_len=platform_max_filepath_len,
            platform=platform,
            max_filename_len=max_filename_len,
            max_filepath_len=max_filepath_len,
        )

        if null_value_handler is None:
            null_value_handler = NullValueHandler.return_null_string
        self._null_value_handler = null_value_handler

        if reserved_name_handler is None:
            reserved_name_handler = ReservedNameHandler.add_trailing_underscore
        self._reserved_name_handler = reserved_name_handler

        self._validate_after_sanitize = validate_after_sanitize

        self._validator = validator

    @abc.abstractmethod
    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:  # pragma: no cover
        pass


class BaseValidator(AbstractValidator):
    @property
    def min_len(self) -> int:
        return self._min_len

    def __init__(
        self,
        min_len: int,
        fs_encoding: Optional[str],
        check_reserved: bool,
        max_filename_len: Optional[int] = None,
        max_filepath_len: Optional[int] = None,
        additional_reserved_names: Optional[Sequence[str]] = None,
        platform_max_filepath_len: Optional[int] = None,
        platform: Optional[PlatformType] = None,
    ) -> None:
        if min_len <= 0:
            min_len = DEFAULT_MIN_LEN
        self._min_len = max(min_len, 1)

        super().__init__(
            fs_encoding=fs_encoding,
            max_filename_len=max_filename_len,
            max_filepath_len=max_filepath_len,
            check_reserved=check_reserved,
            additional_reserved_names=additional_reserved_names,
            platform_max_filepath_len=platform_max_filepath_len,
            platform=platform,
        )

        self._validate_max_len()

    def _validate_reserved_keywords(self, name: str) -> None:
        if not self._check_reserved:
            return

        root_name = self.__extract_root_name(name)
        base_name = os.path.basename(name).upper()

        if self._is_reserved_keyword(root_name.upper()) or self._is_reserved_keyword(
            base_name.upper()
        ):
            raise ReservedNameError(
                f"'{root_name}' is a reserved name",
                reusable_name=False,
                reserved_name=root_name,
                platform=self.platform,
            )

    def _validate_max_len(self) -> None:
        if self.max_filename_len < 1:
            raise ValueError("max_filename_len must be greater or equal to one")

        if self.max_filepath_len < 1:
            raise ValueError("max_filepath_len must be greater or equal to one")

        if self.min_len > self.max_filename_len:
            raise ValueError("min_len must be lower than max_filename_len")

    @staticmethod
    def __extract_root_name(path: str) -> str:
        return os.path.splitext(os.path.basename(path))[0]
