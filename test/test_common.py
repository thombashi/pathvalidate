"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import itertools

import pytest
from tcolorpy import tcolor

from pathvalidate import (
    ascii_symbols,
    replace_ansi_escape,
    replace_unprintable_char,
    unprintable_ascii_chars,
)

from ._common import alphanum_chars


class Test_replace_unprintable_char:
    TARGET_CHARS = unprintable_ascii_chars
    NOT_TARGET_CHARS = alphanum_chars + ascii_symbols
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
        ]
        + [
            ["", "", ""],
        ],
    )
    def test_normal(self, value, replace_text, expected):
        assert replace_unprintable_char(value, replace_text) == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [None, TypeError],
            [1, TypeError],
            [True, TypeError],
        ],
    )
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            replace_unprintable_char(value)


class Test_replace_ansi_escape:
    def test_normal(self):
        value = "test"
        ansi_value = tcolor(value, color="ffffff", bg_color="111111", styles=["bold"])
        assert replace_ansi_escape(ansi_value) == value
