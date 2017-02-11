# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import abc

from mbstrdecoder import MultiByteStrDecoder
import pytypeutil
import six

from ._error import NullNameError


def _validate_null_string(text, error_msg="null name"):
    if pytypeutil.is_not_empty_string(text):
        return

    if pytypeutil.is_empty_string(text):
        raise NullNameError(error_msg)

    raise TypeError("text must be a string")


@six.add_metaclass(abc.ABCMeta)
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
    def _unicode_str(self):
        return MultiByteStrDecoder(self._value).unicode_str

    def __init__(self, value):
        self._validate_null_string(value)

        self._value = value.strip()

    def _is_reserved_keyword(self, value):
        return value in self.reserved_keywords

    @staticmethod
    def _validate_null_string(text, error_msg="null name"):
        _validate_null_string(text)
