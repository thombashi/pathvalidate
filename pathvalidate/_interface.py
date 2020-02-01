"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
from typing import Tuple

from ._common import PathType, validate_null_string
from .error import ValidationError


class NameSanitizer(object, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def reserved_keywords(self) -> Tuple[str, ...]:  # pragma: no cover
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

    @abc.abstractmethod
    def sanitize(self, value: PathType, replacement_text: str = "") -> PathType:  # pragma: no cover
        pass

    def _is_reserved_keyword(self, value: str) -> bool:
        return value in self.reserved_keywords

    @staticmethod
    def _validate_null_string(text: PathType) -> None:
        validate_null_string(text)
