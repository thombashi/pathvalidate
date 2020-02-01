"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
import itertools
import re
from typing import Any, List, Optional, Tuple, cast

from ._common import (
    PathType,
    Platform,
    PlatformType,
    is_pathlike_obj,
    normalize_platform,
    preprocess,
    unprintable_ascii_chars,
    validate_pathtype,
)
from ._const import _NTFS_RESERVED_FILE_NAMES
from .error import ValidationError


class Base:
    _INVALID_PATH_CHARS = "".join(unprintable_ascii_chars)
    _INVALID_FILENAME_CHARS = _INVALID_PATH_CHARS + "/"
    _INVALID_WIN_PATH_CHARS = _INVALID_PATH_CHARS + ':*?"<>|\t\n\r\x0b\x0c'
    _INVALID_WIN_FILENAME_CHARS = _INVALID_FILENAME_CHARS + _INVALID_WIN_PATH_CHARS + "\\"

    _WINDOWS_RESERVED_FILE_NAMES = ("CON", "PRN", "AUX", "CLOCK$", "NUL") + tuple(
        "{:s}{:d}".format(name, num)
        for name, num in itertools.product(("COM", "LPT"), range(1, 10))
    )

    _RE_INVALID_FILENAME = re.compile(
        "[{:s}]".format(re.escape(_INVALID_FILENAME_CHARS)), re.UNICODE
    )
    _RE_INVALID_WIN_FILENAME = re.compile(
        "[{:s}]".format(re.escape(_INVALID_WIN_FILENAME_CHARS)), re.UNICODE
    )

    _RE_INVALID_PATH = re.compile("[{:s}]".format(re.escape(_INVALID_PATH_CHARS)), re.UNICODE)
    _RE_INVALID_WIN_PATH = re.compile(
        "[{:s}]".format(re.escape(_INVALID_WIN_PATH_CHARS)), re.UNICODE
    )
    _RE_NTFS_RESERVED = re.compile(
        "|".join("^/{}$".format(re.escape(pattern)) for pattern in _NTFS_RESERVED_FILE_NAMES),
        re.IGNORECASE,
    )

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


class AbstractValidator(Base, metaclass=abc.ABCMeta):
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


class AbstractSanitizer(Base, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:  # pragma: no cover
        pass
