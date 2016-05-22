# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import re

import dataproperty


__INVALID_PATH_CHARS = '\:*?"<>|'
__INVALID_VAR_CHARS = __INVALID_PATH_CHARS + "!#$&'=~^@`[]+-;{},.()%"
__RESERVED_KEYWORDS = [
    "and", "del", "from", "not", "while",
    "as", "elif", "global", "or", "with",
    "assert", "else", "if", "pass", "yield",
    "break", "except", "import", "print",
    "class", "exec", "in", "raise",
    "continue", "finally", "is", "return",
    "def", "for", "lambda", "try",
]


def validate_filename(filename):
    """
    :param str filename: Filename to validate.
    :raises ValueError:
        If the ``filename`` is empty or includes invalid char(s):
        |invalid_path_chars|.
    """

    if dataproperty.is_empty_string(filename):
        raise ValueError("null name")

    match = re.search("[%s]" % (
        re.escape(__INVALID_PATH_CHARS)), filename)
    if match is not None:
        raise ValueError(
            "invalid char found in the file path: '%s'" % (
                re.escape(match.group())))


def validate_python_var_name(var_name):
    """
    Replace invalid characters for a python variable name within
    the ``var_name`` with the ``replacement_text``.
    Invalid characters are as follows: |invalid_var_name_chars|.

    :param str var_name: Variable name to validate.
    :raises ValueError: If
        a) the ``var_name`` is empty.
        b) includes invalid char(s): |invalid_path_chars|.
        c) ``var_name`` is start from digits or symbols (except ``"_"``).
    """

    if dataproperty.is_empty_string(var_name):
        raise ValueError("null name")

    match = re.search("[%s]" % (
        re.escape(__INVALID_VAR_CHARS)), var_name)
    if match is not None:
        raise ValueError(
            "invalid char found in the variable name: '%s'" % (
                re.escape(match.group())))

    match = re.search("^[0-9%s]" % (
        re.escape(__INVALID_VAR_CHARS)), var_name)
    if match is not None:
        raise ValueError(
            "the first char of the variable name is invalid: '%s'" % (
                re.escape(match.group())))

    if var_name in __RESERVED_KEYWORDS:
        raise ValueError(
            "%s is a reserved keyword by pyhon" % (var_name))


def sanitize_filename(filename, replacement_text=""):
    """
    Replace invalid characters for a file path within the ``filename``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_path_chars|.

    :param str filename: Filename to validate.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    filename = filename.strip()
    re_replace = re.compile("[%s]" % re.escape(__INVALID_PATH_CHARS))

    return re_replace.sub(replacement_text, filename)


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Replace invalid characters for a python variable name within
    the ``var_name`` with the ``replacement_text``.
    Invalid characters are as follows: |invalid_var_name_chars|.

    :param str filename: Filename to validate.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the replacement string is invalid.

    .. seealso::

        :py:func:`.validate_python_var_name`
    """

    var_name = var_name.strip()
    re_replace = re.compile("[%s]" % re.escape(__INVALID_VAR_CHARS))

    sanitize_var_name = re_replace.sub(replacement_text, var_name)

    validate_python_var_name(sanitize_var_name)

    return sanitize_var_name


def replace_symbol(filename, replacement_text=""):
    fname = sanitize_filename(filename, replacement_text)
    if fname is None:
        return None

    re_replace = re.compile("[%s]" % re.escape(" ,.%()/"))

    return re_replace.sub(replacement_text, fname)
