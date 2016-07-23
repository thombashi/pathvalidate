# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import itertools
import random
import string

import pytest

from pathvalidate import *


random.seed(0)

char_list = [x for x in string.digits + string.ascii_letters]

INVALID_PATH_CHARS = [
    "\\", ":", "*", "?", '"', "<", ">", "|",
]
INVALID_FILENAME_CHARS = INVALID_PATH_CHARS + ["/"]
INVALID_VAR_CHARS = INVALID_FILENAME_CHARS + [
    "!", "#", "$", '&', "'",
    "=", "~", "^", "@", "`", "[", "]", "+", "-", ";", "{", "}",
    ",", ".", "(", ")", "%",
    " ", "\t", "\n", "\r", "\f", "\v",
]
INVALID_EXCEL_CHARS = [
    "[", "]", ":", "*", "?", "/", "\\",
]
VALID_FILENAME_CHARS = [
    "!", "#", "$", '&', "'", "_",
    "=", "~", "^", "@", "`", "[", "]", "+", "-", ";", "{", "}",
    ",", ".", "(", ")", "%",
]
VALID_PATH_CHARS = VALID_FILENAME_CHARS + ["/"]
RESERVED_KEYWORDS = [
    "and", "del", "from", "not", "while",
    "as", "elif", "global", "or", "with",
    "assert", "else", "if", "pass", "yield",
    "break", "except", "import", "print",
    "class", "exec", "in", "raise",
    "continue", "finally", "is", "return",
    "def", "for", "lambda", "try",
    "False", "True", "None", "NotImplemented", "Ellipsis",
]


def make_random_str(length):
    return "".join([random.choice(char_list) for _i in range(length)])


class Test_validate_filename:
    VALID_CHAR_LIST = VALID_FILENAME_CHARS
    INVALID_CHAR_LIST = INVALID_FILENAME_CHARS

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_filename(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in INVALID_CHAR_LIST
    ])
    def test_exception_0(self, value):
        with pytest.raises(ValueError):
            validate_filename(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_1(self, value, expected):
        with pytest.raises(expected):
            validate_filename(value)


class Test_validate_file_path:
    VALID_CHAR_LIST = VALID_PATH_CHARS
    INVALID_CHAR_LIST = INVALID_PATH_CHARS

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_file_path(value)

    @pytest.mark.parametrize(["value"], [
        [make_random_str(64) + invalid_char + make_random_str(64)]
        for invalid_char in INVALID_CHAR_LIST
    ])
    def test_exception_0(self, value):
        with pytest.raises(ValueError):
            validate_file_path(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_1(self, value, expected):
        with pytest.raises(expected):
            validate_file_path(value)


class Test_validate_python_var_name:
    VALID_CHAR_LIST = [
        c for c in string.digits + string.ascii_letters + "_"
    ]
    INVALID_CHAR_LIST = INVALID_VAR_CHARS

    @pytest.mark.parametrize(["value"], [
        ["abc" + valid_char + "hoge123"]
        for valid_char in VALID_CHAR_LIST
    ])
    def test_normal(self, value):
        validate_python_var_name(value)

    @pytest.mark.parametrize(["value"], [
        ["abc" + invalid_char + "hoge123"]
        for invalid_char in INVALID_CHAR_LIST
    ])
    def test_exception_invalid_char(self, value):
        with pytest.raises(ValueError):
            validate_python_var_name(value)

    @pytest.mark.parametrize(["value"], [
        [invalid_char + "hoge123"]
        for invalid_char in string.digits + "_"
    ])
    def test_exception_invalid_first_char(self, value):
        with pytest.raises(ValueError):
            validate_python_var_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            validate_python_var_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [reserved_keyword, ValueError]
        for reserved_keyword in RESERVED_KEYWORDS + ["__debug__"]
    ])
    def test_exception_reserved(self, value, expected):
        with pytest.raises(expected):
            validate_python_var_name(value)


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


class Test_sanitize_filename:
    SANITIZE_CHAR_LIST = INVALID_FILENAME_CHARS
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
    SANITIZE_CHAR_LIST = INVALID_PATH_CHARS
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


class Test_sanitize_python_var_name:
    SANITIZE_CHAR_LIST = INVALID_VAR_CHARS
    NOT_SANITIZE_CHAR_LIST = ["_"]
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
        sanitized_name = sanitize_python_var_name(value, replace_text)
        assert sanitized_name == expected
        validate_python_var_name(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [invalid_char + "hoge_123", "_", "hoge_123"]
            for invalid_char in string.digits + "_"
        ] + [
            [invalid_char + "hoge_123", "a", "ahoge_123"]
            for invalid_char in string.digits + "_"
        ]
    )
    def test_normal_invalid_first_char_x1(self, value, replace_text, expected):
        sanitized_name = sanitize_python_var_name(value, replace_text)
        assert sanitized_name == expected
        validate_python_var_name(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [invalid_char * 2 + "hoge_123", "_", "hoge_123"]
            for invalid_char in string.digits + "_"
        ] + [
            [invalid_char * 2 + "hoge_123", "a", "aahoge_123"]
            for invalid_char in string.digits + "_"
        ]
    )
    def test_normal_invalid_first_char_x2(self, value, replace_text, expected):
        sanitized_name = sanitize_python_var_name(value, replace_text)
        assert sanitized_name == expected
        validate_python_var_name(sanitized_name)

    @pytest.mark.parametrize(["value", "expected"], [
        [reserved_keyword, ValueError]
        for reserved_keyword in RESERVED_KEYWORDS
    ])
    def test_exception_reserved(self, value, expected):
        with pytest.raises(expected):
            sanitize_python_var_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_python_var_name(value)


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


class Test_replace_symbol:
    TARGET_CHAR_LIST = INVALID_VAR_CHARS
    NOT_TARGET_CHAR_LIST = char_list
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in itertools.product(
                TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in itertools.product(
                NOT_TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + reserved_keyword + "B", rep, "A" + reserved_keyword + "B"]
            for reserved_keyword, rep in itertools.product(
                RESERVED_KEYWORDS, REPLACE_TEXT_LIST)

        ]
    )
    def test_normal(self, value, replace_text, expected):
        assert replace_symbol(value, replace_text) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [True, TypeError],
    ])
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            replace_symbol(value)
