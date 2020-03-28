"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import itertools

import pytest

from pathvalidate import sanitize_ltsv_label, validate_ltsv_label
from pathvalidate.error import ErrorReason, ValidationError

from ._common import INVALID_WIN_FILENAME_CHARS, alphanum_chars


VALID_LABEL_CHARS = alphanum_chars + ("_", ".", "-")
INVALID_LABEL_CHARS = INVALID_WIN_FILENAME_CHARS + (
    "!",
    "#",
    "$",
    "&",
    "'",
    "=",
    "~",
    "^",
    "@",
    "`",
    "[",
    "]",
    "+",
    ";",
    "{",
    "}",
    ",",
    "(",
    ")",
    "%",
    " ",
    "\t",
    "\n",
    "\r",
    "\f",
    "\v",
)


class Test_validate_ltsv_label:
    VALID_CHARS = alphanum_chars
    INVALID_CHARS = INVALID_LABEL_CHARS

    @pytest.mark.parametrize(
        ["value"], [["abc" + valid_char + "hoge123"] for valid_char in VALID_CHARS]
    )
    def test_normal(self, value):
        validate_ltsv_label(value)

    @pytest.mark.parametrize(
        ["value"],
        [["abc" + invalid_char + "hoge123"] for invalid_char in INVALID_CHARS]
        + [["あいうえお"], ["ラベル"]],
    )
    def test_exception_invalid_char(self, value):
        with pytest.raises(ValidationError) as e:
            validate_ltsv_label(value)
        assert e.value.reason == ErrorReason.INVALID_CHARACTER


class Test_sanitize_ltsv_label:
    TARGET_CHARS = INVALID_LABEL_CHARS
    NOT_TARGET_CHARS = alphanum_chars
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in itertools.product(TARGET_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in itertools.product(NOT_TARGET_CHARS, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal(self, value, replace_text, expected):
        assert sanitize_ltsv_label(value, replace_text) == expected

    @pytest.mark.parametrize(["value", "expected"], [["aあいbうえcお", "abc"]])
    def test_normal_multibyte(self, value, expected):
        sanitize_ltsv_label(value)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [["", ValidationError], [None, ValidationError], [1, TypeError], [True, TypeError]],
    )
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            sanitize_ltsv_label(value)
