# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from .error import NullNameError


def _validate_null_string(text, error_msg="null name"):
    if is_not_null_string(text):
        return

    if is_null_string(text):
        raise NullNameError(error_msg)

    raise TypeError("text must be a string: actual={}".format(type(text)))


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


def get_unprintable_ascii_char_list():
    import six
    import string

    return [six.unichr(c) for c in range(128) if chr(c) not in string.printable]


unprintable_ascii_char_list = get_unprintable_ascii_char_list()
