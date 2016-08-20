# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import itertools
import random

import pytest

from pathvalidate import *

from ._common import make_random_str
from .test_pathvalidate import VALID_PATH_CHARS


random.seed(0)

INVALID_EXCEL_CHARS = [
    "[", "]", ":", "*", "?", "/", "\\",
]


class Test_validate_excel_sheet_name:
    VALID_CHAR_LIST = set(VALID_PATH_CHARS).difference(
        set(INVALID_EXCEL_CHARS))
    INVALID_CHAR_LIST = INVALID_EXCEL_CHARS

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_excel_sheet_name(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in INVALID_CHAR_LIST
    ])
    def test_exception_0(self, value):
        with pytest.raises(ValueError):
            validate_excel_sheet_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_1(self, value, expected):
        with pytest.raises(expected):
            validate_excel_sheet_name(value)


class Test_sanitize_excel_sheet_name:
    SANITIZE_CHAR_LIST = INVALID_EXCEL_CHARS
    NOT_SANITIZE_CHAR_LIST = set(VALID_PATH_CHARS).difference(
        set(INVALID_EXCEL_CHARS))
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in itertools.product(
                SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in itertools.product(
                NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
    )
    def test_normal(self, value, replace_text, expected):
        sanitized_name = sanitize_excel_sheet_name(value, replace_text)
        assert sanitized_name == expected
        validate_excel_sheet_name(sanitized_name)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_excel_sheet_name(value)
