# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import re
import string

import dataproperty


__INVALID_PATH_CHARS = '\:*?"<>|'
__INVALID_FILENAME_CHARS = __INVALID_PATH_CHARS + "/"
__INVALID_EXCEL_CHARS = "[]:*?/\\"

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

__RE_INVALID_FILENAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_FILENAME_CHARS)))
__RE_INVALID_PATH = re.compile(
    "[{:s}]".format(re.escape(__INVALID_PATH_CHARS)))
__RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_]")
__RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z]+")
__RE_INVALID_EXCEL_SHEET_NAME = re.compile(
    "[{:s}]".format(re.escape(__INVALID_EXCEL_CHARS)))

__RE_SYMBOL = re.compile("[^a-zA-Z0-9]")


def __validate_null_string(text):
    if dataproperty.is_empty_string(text):
        raise ValueError("null name")


def validate_filename(filename):
    """
    :param str filename: Filename to validate.
    :raises ValueError:
        If the ``filename`` is empty or includes invalid char(s):
        |invalid_filename_chars|.
    """

    __validate_null_string(filename)

    match = __RE_INVALID_FILENAME.search(filename)
    if match is not None:
        raise ValueError(
            "invalid char found in the filename: '{:s}'".format(
                re.escape(match.group())))


def validate_file_path(file_path):
    """
    :param str filename: File path to validate.
    :raises ValueError:
        If the ``file_path`` is empty or includes invalid char(s):
        |invalid_file_path_chars|.
    """

    __validate_null_string(file_path)

    match = __RE_INVALID_PATH.search(file_path)
    if match is not None:
        raise ValueError(
            "invalid char found in the file path: '{:s}'".format(
                re.escape(match.group())))


def validate_python_var_name(var_name):
    """
    :param str var_name: Name to validate.
    :raises ValueError: If the ``var_name`` is
        **a)** empty.
        **b)** invalid as
        `Python identifier <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`__.
        **c)** equals to
        `reserved keywords <https://docs.python.org/3/reference/lexical_analysis.html#keywords>`__ or
        `built-in constants <https://docs.python.org/3/library/constants.html>`__.
    """

    __validate_null_string(var_name)

    if var_name in __RESERVED_KEYWORDS + __BUILT_CONSTANTS:
        raise ValueError(
            "{:s} is a reserved keyword by pyhon".format(var_name))

    match = __RE_INVALID_VAR_NAME.search(var_name)
    if match is not None:
        raise ValueError(
            "invalid char found in the variable name: '{:s}'".format(
                re.escape(match.group())))

    match = __RE_INVALID_VAR_NAME_HEAD.search(var_name)
    if match is not None:
        raise ValueError(
            "the first char of the variable name is invalid: '{:s}'".format(
                re.escape(match.group())))


def validate_excel_sheet_name(sheet_name):
    """
    :param str sheet_name: Excel sheet name to validate.
    :raises ValueError:
        If the ``sheet_name`` is empty or includes invalid char(s):
        |invalid_excel_sheet_chars|.
    """

    __validate_null_string(sheet_name)

    match = __RE_INVALID_EXCEL_SHEET_NAME.search(sheet_name)
    if match is not None:
        raise ValueError(
            "invalid char found in the sheet name: '{:s}'".format(
                re.escape(match.group())))


def sanitize_filename(filename, replacement_text=""):
    """
    Replace invalid characters for a filename within the ``filename``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_filename_chars|.

    :param str filename: Filename to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``filename`` is a invalid filename.
    """

    try:
        return __RE_INVALID_FILENAME.sub(replacement_text, filename.strip())
    except AttributeError as e:
        raise ValueError(e)


def sanitize_file_path(file_path, replacement_text=""):
    """
    Replace invalid characters for a file path within the ``file_path``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_file_path_chars|.

    :param str file_path: File path to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``file_path`` is a invalid file path.
    """

    try:
        return __RE_INVALID_PATH.sub(replacement_text, file_path.strip())
    except AttributeError as e:
        raise ValueError(e)


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Replace invalid characters for a Python variable name within
    the ``var_name`` with the ``replacement_text``.
    Invalid chars of the beginning of the variable name will be deleted.

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


def sanitize_excel_sheet_name(sheet_name, replacement_text=""):
    """
    Replace invalid characters for a Excel sheet name within the ``sheet_name``
    with the ``replacement_text``. Invalid characters are as follows:
    |invalid_excel_sheet_chars|.

    :param str sheet_name: Excel sheet name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    return __RE_INVALID_EXCEL_SHEET_NAME.sub(
        replacement_text, sheet_name.strip())


def replace_symbol(text, replacement_text=""):
    """
    Replace all of the symbols.

    :param str text: Input text.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    return __RE_SYMBOL.sub(replacement_text, text)
