# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import itertools

import pytest
from pathvalidate import (
    InvalidCharError,
    ascii_symbol_list,
    replace_symbol,
    unprintable_ascii_char_list,
    validate_symbol,
)

from ._common import alphanum_char_list


class Test_validate_symbol(object):
    VALID_CHAR_LIST = alphanum_char_list
    INVALID_CHAR_LIST = ascii_symbol_list

    @pytest.mark.parametrize(
        ["value"], [["abc" + valid_char + "hoge123"] for valid_char in VALID_CHAR_LIST]
    )
    def test_normal(self, value):
        validate_symbol(value)

    @pytest.mark.parametrize(["value"], [["あいうえお"], ["シート"]])
    def test_normal_multibyte(self, value):
        pytest.skip("TODO")

        validate_symbol(value)

    @pytest.mark.parametrize(
        ["value"],
        [
            ["abc" + invalid_char + "hoge123"]
            for invalid_char in INVALID_CHAR_LIST + unprintable_ascii_char_list
        ],
    )
    def test_exception_invalid_char(self, value):
        with pytest.raises(InvalidCharError):
            validate_symbol(value)


class Test_replace_symbol(object):
    TARGET_CHAR_LIST = ascii_symbol_list
    NOT_TARGET_CHAR_LIST = alphanum_char_list
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
        assert replace_symbol(value, replace_text) == expected

    @pytest.mark.parametrize(
        ["value", "replace_text", "is_replace_consecutive_chars", "is_strip", "expected"],
        [
            ["!a##b$$$c((((d]]]])", "_", True, True, "a_b_c_d"],
            ["!a##b$$$c((((d]]]])", "_", True, False, "_a_b_c_d_"],
            ["!a##b$$$c((((d]]]])", "_", False, True, "a__b___c____d"],
            ["!a##b$$$c((((d]]]])", "_", False, False, "_a__b___c____d_____"],
        ],
    )
    def test_normal_consecutive(
        self, value, replace_text, is_replace_consecutive_chars, is_strip, expected
    ):
        assert (
            replace_symbol(value, replace_text, is_replace_consecutive_chars, is_strip) == expected
        )

    @pytest.mark.parametrize(
        ["value", "expected"], [[None, TypeError], [1, TypeError], [True, TypeError]]
    )
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            replace_symbol(value)
