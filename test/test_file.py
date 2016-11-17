# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import itertools
import platform
import random

import pytest

from pathvalidate import *

from ._common import make_random_str
from ._common import INVALID_PATH_CHARS
from ._common import INVALID_FILENAME_CHARS
from ._common import INVALID_WIN_PATH_CHARS
from ._common import INVALID_WIN_FILENAME_CHARS
from ._common import VALID_FILENAME_CHARS
from ._common import VALID_PATH_CHARS


random.seed(0)


WIN_RESERVED_FILE_NAME_LIST = [
    "CON", "con",
    "PRN", "prn",
    "AUX", "aux",
    "NUL", "nul",
] + [
    "{:s}{:d}".format(name, num)
    for name, num
    in itertools.product(["COM", "com", "LPT", "lpt"], range(1, 10))
]


UTF8_NAME_LIST = [
    ["あいうえお.txt"],
    ["属性.txt"],
]


class Test_validate_filename:
    VALID_CHAR_LIST = VALID_FILENAME_CHARS
    INVALID_CHAR_LIST = INVALID_WIN_FILENAME_CHARS

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_filename(value)

    @pytest.mark.parametrize(["value"], UTF8_NAME_LIST)
    def test_normal_utf8(self, value):
        validate_filename(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in INVALID_FILENAME_CHARS
    ])
    def test_exception_invalid_char(self, value):
        with pytest.raises(InvalidCharError):
            validate_filename(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in set(INVALID_WIN_PATH_CHARS).difference(
            set(INVALID_PATH_CHARS + INVALID_FILENAME_CHARS))
    ])
    def test_exception_invalid_win_char(self, value):
        with pytest.raises(InvalidCharWindowsError):
            validate_filename(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [reserved_keyword, InvalidReservedNameError]
        for reserved_keyword in WIN_RESERVED_FILE_NAME_LIST
    ])
    def test_exception_reserved(self, value, expected):
        with pytest.raises(expected):
            validate_filename(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, NullNameError],
        ["", NullNameError],
        ["a" * 256, InvalidLengthError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filename(value)


class Test_validate_file_path:
    VALID_CHAR_LIST = VALID_PATH_CHARS

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_file_path(value)

    @pytest.mark.parametrize(["value"], UTF8_NAME_LIST)
    def test_normal_utf8(self, value):
        validate_file_path("/tmp/{}".format(value))

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in INVALID_PATH_CHARS
    ])
    def test_exception_invalid_char(self, value):
        with pytest.raises(InvalidCharError):
            validate_file_path(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in set(INVALID_WIN_PATH_CHARS).difference(
            set(INVALID_PATH_CHARS))
    ])
    def test_exception_invalid_win_char(self, value):
        with pytest.raises(InvalidCharWindowsError):
            validate_file_path(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, NullNameError],
        ["", NullNameError],
        ["a" * 1025, InvalidLengthError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_file_path(value)


@pytest.mark.skipif("platform.system() != 'Windows'")
class Test_validate_win_file_path:
    VALID_CHAR_LIST = VALID_PATH_CHARS

    @pytest.mark.parametrize(["value"], [
        ['C:\\Users\\test\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\test_exception__hoge_csv_heade1\\hoge.csv'],
        ['Z:\\Users\\test\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\test_exception__hoge_csv_heade1\\hoge.csv'],
        ['C:/Users/test/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv'],
        ['C:\\Users/test\\AppData/Local\\Temp/pytest-of-test\\pytest-0/test_exception__hoge_csv_heade1\\hoge.csv'],
        ['C:\\Users'],
        ['C:\\'],
        ['\\Users'],
    ])
    def test_normal(self, value):
        validate_file_path(value)


class Test_sanitize_filename:
    SANITIZE_CHAR_LIST = INVALID_WIN_FILENAME_CHARS
    NOT_SANITIZE_CHAR_LIST = VALID_FILENAME_CHARS
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
        sanitized_name = sanitize_filename(value, replace_text)
        assert sanitized_name == expected
        validate_filename(sanitized_name)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filename(value)


class Test_sanitize_file_path:
    SANITIZE_CHAR_LIST = INVALID_WIN_PATH_CHARS
    NOT_SANITIZE_CHAR_LIST = VALID_PATH_CHARS
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
        sanitized_name = sanitize_file_path(value, replace_text)
        assert sanitized_name == expected
        validate_file_path(sanitized_name)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_file_path(value)
