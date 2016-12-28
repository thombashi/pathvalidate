# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

import dataproperty
from mbstrdecoder import MultiByteStrDecoder

from ._common import _validate_null_string
from ._error import (
    InvalidCharError,
    InvalidReservedNameError,
    NullNameError
)


__PYTHON_RESERVED_KEYWORDS = [
    "and", "del", "from", "not", "while",
    "as", "elif", "global", "or", "with",
    "assert", "else", "if", "pass", "yield",
    "break", "except", "import", "print",
    "class", "exec", "in", "raise",
    "continue", "finally", "is", "return",
    "def", "for", "lambda", "try",
]
__PYTHON_BUILT_CONSTANTS = [
    "False", "True", "None", "NotImplemented", "Ellipsis", "__debug__",
]

__RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_]")
__RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z]+")


def validate_python_var_name(var_name):
    """
    :param str var_name: Name to validate.
    :raises pathvalidate.NullNameError: If the ``var_name`` is empty.
    :raises pathvalidate.InvalidCharError: If the ``var_name`` is invalid as
        `Python identifier
        <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`__.
    :raises pathvalidate.InvalidReservedNameError:
        If the ``var_name`` is equals to
        `Python reserved keywords
        <https://docs.python.org/3/reference/lexical_analysis.html#keywords>`__
        or
        `Python built-in constants
        <https://docs.python.org/3/library/constants.html>`__.
    """

    _validate_null_string(var_name)

    if var_name in __PYTHON_RESERVED_KEYWORDS + __PYTHON_BUILT_CONSTANTS:
        raise InvalidReservedNameError(
            "{:s} is a reserved keyword by pyhon".format(var_name))

    unicode_var_name = MultiByteStrDecoder(var_name).unicode_str

    match = __RE_INVALID_VAR_NAME.search(unicode_var_name)
    if match is not None:
        raise InvalidCharError(
            "invalid char found in the variable name: '{}'".format(
                re.escape(match.group())))

    match = __RE_INVALID_VAR_NAME_HEAD.search(unicode_var_name)
    if match is not None:
        raise InvalidCharError(
            "the first character of the variable name is invalid: '{}'".format(
                re.escape(match.group())))


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Make a valid Python variable name from ``var_name``.

    To make a valid name:

    - Replace invalid characters for a Python variable name within
      the ``var_name`` with the ``replacement_text``
    - Delete invalid chars for the beginning of the variable name
    - Append under bar at the tail of the name if sanitized name
      is one of the Python reserved names

    :param str filename: Name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If ``var_name`` or ``replacement_text`` is invalid.

    .. seealso::

        :py:func:`.validate_python_var_name`
    """

    try:
        var_name = var_name.strip()
    except AttributeError as e:
        raise ValueError(e)

    sanitize_var_name = __RE_INVALID_VAR_NAME.sub(
        replacement_text, MultiByteStrDecoder(var_name).unicode_str)

    # delete invalid char(s) in the beginning of the variable name
    is_delete_head = any([
        dataproperty.is_empty_string(replacement_text),
        __RE_INVALID_VAR_NAME_HEAD.search(replacement_text) is not None,
    ])

    if is_delete_head:
        sanitize_var_name = __RE_INVALID_VAR_NAME_HEAD.sub(
            "", sanitize_var_name)
    else:
        match = __RE_INVALID_VAR_NAME_HEAD.search(sanitize_var_name)
        if match is not None:
            sanitize_var_name = (
                match.end() * replacement_text +
                __RE_INVALID_VAR_NAME_HEAD.sub("", sanitize_var_name)
            )

    try:
        validate_python_var_name(sanitize_var_name)
    except InvalidReservedNameError:
        sanitize_var_name += u"_"
    except NullNameError:
        pass

    return sanitize_var_name
