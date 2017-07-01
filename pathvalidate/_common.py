# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import abc

from ._error import NullNameError
from ._six import add_metaclass


def _validate_null_string(text, error_msg="null name"):
    if is_not_null_string(text):
        return

    if is_null_string(text):
        raise NullNameError(error_msg)

    raise TypeError("text must be a string")


def _preprocess(name):
    return name.strip()


def is_null_string(value):
    if value is None:
        return True

    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def is_not_null_string(value):
    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


@add_metaclass(abc.ABCMeta)
class NameSanitizer(object):

    @abc.abstractproperty
    def reserved_keywords(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def validate(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def sanitize(self, replacement_text=""):  # pragma: no cover
        pass

    @property
    def _str(self):
        return self._value

    def __init__(self, value):
        self._validate_null_string(value)

        self._value = value.strip()

    def _is_reserved_keyword(self, value):
        return value in self.reserved_keywords

    @staticmethod
    def _validate_null_string(text, error_msg="null name"):
        _validate_null_string(text)
