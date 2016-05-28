# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import re
import string

import dataproperty


__INVALID_PATH_CHARS = '\:*?"<>|'
__INVALID_FILENAME_CHARS = __INVALID_PATH_CHARS + "/"
__RESERVED_KEYWORDS = [
    "and", "del", "from", "not", "while",
    "as", "elif", "global", "or", "with",
    "assert", "else", "if", "pass", "yield",
    "break", "except", "import", "print",
    "class", "exec", "in", "raise",
    "continue", "finally", "is", "return",
    "def", "for", "lambda", "try",
]
__BUILT_CONSTANTS = [
    "False", "True", "None", "NotImplemented", "Ellipsis", "__debug__",
]

__RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_]")
__RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z]+")


def validate_filename(filename):
    """
    :param str filename: Filename to validate.
    :raises ValueError:
        If the ``filename`` is empty or includes invalid char(s):
        |invalid_filename_chars|.
    """

    if dataproperty.is_empty_string(filename):
        raise ValueError("null name")

    match = re.search("[%s]" % (
        re.escape(__INVALID_FILENAME_CHARS)), filename)
    if match is not None:
        raise ValueError(
            "invalid char found in the file path: '%s'" % (
                re.escape(match.group())))


def validate_python_var_name(var_name):
    """
    :param str var_name: Variable name to validate.
    :raises ValueError: If the ``var_name`` is
        **a)** empty.
        **b)** invalid as
        `Python identifier <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`__.
        **c)** equals to
        `reserved keywords <https://docs.python.org/3/reference/lexical_analysis.html#keywords>`__ or
        `built-in constants <https://docs.python.org/3/library/constants.html>`__.
    """

    if dataproperty.is_empty_string(var_name):
        raise ValueError("null name")

    if var_name in __RESERVED_KEYWORDS + __BUILT_CONSTANTS:
        raise ValueError(
            "%s is a reserved keyword by pyhon" % (var_name))

    match = __RE_INVALID_VAR_NAME.search(var_name)
    if match is not None:
        raise ValueError(
            "invalid char found in the variable name: '%s'" % (
                re.escape(match.group())))

    match = __RE_INVALID_VAR_NAME_HEAD.search(var_name)
    if match is not None:
        raise ValueError(
            "the first char of the variable name is invalid: '%s'" % (
                re.escape(match.group())))


def sanitize_filename(filename, replacement_text=""):
    """
    Replace invalid characters for a file path within the ``filename``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_filename_chars|.

    :param str filename: Filename to validate.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    filename = filename.strip()
    re_replace = re.compile("[%s]" % re.escape(__INVALID_FILENAME_CHARS))

    return re_replace.sub(replacement_text, filename)


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Replace invalid characters for a Python variable name within
    the ``var_name`` with the ``replacement_text``.
    Invalid chars of the beginning of the variable name will be deleted.

    :param str filename: Filename to validate.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the replacement string is invalid.

    .. seealso::

        :py:func:`.validate_python_var_name`
    """

    var_name = var_name.strip()
    sanitize_var_name = __RE_INVALID_VAR_NAME.sub(
        replacement_text, var_name)

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

    validate_python_var_name(sanitize_var_name)

    return sanitize_var_name


def replace_symbol(filename, replacement_text=""):
    fname = sanitize_filename(filename, replacement_text)
    if fname is None:
        return None

    re_replace = re.compile("[%s]" % re.escape(" ,.%()/"))

    return re_replace.sub(replacement_text, fname)
