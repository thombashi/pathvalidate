# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import abc
import re

import dataproperty as dp
from mbstrdecoder import MultiByteStrDecoder

from ._common import NameSanitizer
from ._error import (
    InvalidCharError,
    InvalidReservedNameError,
    NullNameError
)


class VarNameSanitizer(NameSanitizer):

    @abc.abstractproperty
    def _invalid_var_name_head_re(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def _invalid_var_name_re(self):  # pragma: no cover
        pass

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        sanitize_var_name = self._invalid_var_name_re.sub(
            replacement_text, self._unicode_str)

        # delete invalid char(s) in the beginning of the variable name
        is_require_remove_head = any([
            dp.is_empty_string(replacement_text),
            self._invalid_var_name_head_re.search(
                replacement_text) is not None,
        ])

        if is_require_remove_head:
            sanitize_var_name = self._invalid_var_name_head_re.sub(
                "", sanitize_var_name)
        else:
            match = self._invalid_var_name_head_re.search(sanitize_var_name)
            if match is not None:
                sanitize_var_name = (
                    match.end() * replacement_text +
                    self._invalid_var_name_head_re.sub("", sanitize_var_name)
                )

        try:
            self._validate(sanitize_var_name)
        except InvalidReservedNameError:
            sanitize_var_name += "_"
        except NullNameError:
            pass

        return sanitize_var_name

    def _validate(self, value):
        self._validate_null_string(value)

        unicode_var_name = MultiByteStrDecoder(value).unicode_str

        if self._is_reserved_keyword(unicode_var_name):
            raise InvalidReservedNameError(
                "{:s} is a reserved keyword by pyhon".format(unicode_var_name))

        match = self._invalid_var_name_re.search(unicode_var_name)
        if match is not None:
            raise InvalidCharError(
                "invalid char found in the variable name: '{}'".format(
                    re.escape(match.group())))

        match = self._invalid_var_name_head_re.search(unicode_var_name)
        if match is not None:
            raise InvalidCharError(
                "the first character of the variable name is invalid: '{}'".format(
                    re.escape(match.group())))
