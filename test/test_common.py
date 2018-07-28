# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import itertools

import pytest
from pathvalidate import ascii_symbol_list, replace_unprintable_char, unprintable_ascii_char_list

from ._common import alphanum_char_list


class Test_replace_unprintable_char(object):
    TARGET_CHAR_LIST = unprintable_ascii_char_list
    NOT_TARGET_CHAR_LIST = alphanum_char_list + ascii_symbol_list
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in itertools.product(TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in itertools.product(NOT_TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [["", "", ""]],
    )
    def test_normal(self, value, replace_text, expected):
        assert replace_unprintable_char(value, replace_text) == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [[None, TypeError], [1, TypeError], [True, TypeError]]
    )
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            replace_unprintable_char(value)
