# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import re

import dataproperty


__INVALID_PATH_CHARS = '\:*?"<>|'
__INVALID_VAR_CHARS = __INVALID_PATH_CHARS + "!#$&'=~^@`[]+-;{},.()%"


def validate_filename(filename):
    """
    :param str filename: Filename to validate.
    :raises ValueError:
        If the ``filename`` is empty or includes invalid char(s):
        (``\``, ``:``, ``*``, ``?``, ``"``, ``<``, ``>``, ``|``).
    """

    if dataproperty.is_empty_string(filename):
        raise ValueError("null path")

    match = re.search("[%s]" % (
        re.escape(__INVALID_PATH_CHARS)), filename)
    if match is not None:
        raise ValueError(
            "invalid char found in the file path: '%s'" % (
                re.escape(match.group())))


def sanitize_filename(filename, replacement_text=""):
    """
    Replace invalid characters for a file path within the ``filename``
    with the ``replacement_text``. Invalid characters are as follows:
    ``\``, ``:``, ``*``, ``?``, ``"``, ``<``, ``>``, ``|``.

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
    Invalid characters are as follows:
    ``\``, ``:``, ``*``, ``?``, ``"``, ``<``, ``>``, ``|``.
    ``"``, ``!``, ``#``, ``$``, ``&``, ``'``, ``=``, ``~``, ``^``, ``@``,
    `````, ``[``, ``]``, ``+``, ``-``, ``;``, ``{``, ``}``, ``,``,
    ``.``, ``(``, ``)``, ``%``.

    :param str filename: Filename to validate.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    var_name = var_name.strip()
    re_replace = re.compile("[%s]" % re.escape(__INVALID_VAR_CHARS))

    return re_replace.sub(replacement_text, var_name)


def replace_symbol(filename, replacement_text=""):
    fname = sanitize_filename(filename, replacement_text)
    if fname is None:
        return None

    re_replace = re.compile("[%s]" % re.escape(" ,.%()/"))

    return re_replace.sub(replacement_text, fname)
