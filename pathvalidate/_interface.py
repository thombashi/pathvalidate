"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import abc

from ._common import validate_null_string
from .error import ValidationError


class NameSanitizer(object, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def reserved_keywords(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def validate(self, value):  # pragma: no cover
        pass

    def is_valid(self, value):
        try:
            self.validate(value)
        except (TypeError, ValidationError):
            return False

        return True

    @abc.abstractmethod
    def sanitize(self, value, replacement_text=""):  # pragma: no cover
        pass

    def _is_reserved_keyword(self, value):
        return value in self.reserved_keywords

    @staticmethod
    def _validate_null_string(text):
        validate_null_string(text, error_msg="null name")
