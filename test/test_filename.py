# encoding: utf-8
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import platform as m_platform  # noqa: W0611
import random
import sys  # noqa: W0611
from itertools import chain, product

import pytest
import six
from faker import Factory
from pathvalidate import (
    InvalidCharError,
    InvalidLengthError,
    NullNameError,
    Platform,
    ReservedNameError,
    sanitize_filename,
    validate_filename,
)
from pathvalidate._common import is_pathlike_obj, unprintable_ascii_chars
from pathvalidate._file import FileNameSanitizer

from ._common import (
    INVALID_FILENAME_CHARS,
    INVALID_PATH_CHARS,
    INVALID_WIN_FILENAME_CHARS,
    INVALID_WIN_PATH_CHARS,
    VALID_FILENAME_CHARS,
    VALID_PLATFORM_NAMES,
    make_random_str,
)


try:
    from pathlib import Path
except ImportError:
    Path = six.text_type


nan = float("nan")
inf = float("inf")

random.seed(0)

VALID_MULTIBYTE_NAMES = ["新しいテキスト ドキュメント.txt", "新規 Microsoft Excel Worksheet.xlsx"]
WIN_RESERVED_FILE_NAMES = [".", "..", "CON", "con", "PRN", "prn", "AUX", "aux", "NUL", "nul"] + [
    "{:s}{:d}".format(name, num)
    for name, num in product(["COM", "com", "LPT", "lpt"], range(1, 10))
]


class Test_FileSanitizer(object):
    @pytest.mark.parametrize(
        ["test_platform", "expected"],
        [["windows", Platform.WINDOWS], ["linux", Platform.LINUX], ["macos", Platform.MACOS]],
    )
    def test_normal_platform_auto(self, monkeypatch, test_platform, expected):
        if test_platform == "windows":
            patch = lambda: "windows"
        elif test_platform == "linux":
            patch = lambda: "linux"
        elif test_platform == "macos":
            patch = lambda: "macos"
        else:
            raise ValueError("unexpected test platform: {}".format(test_platform))

        monkeypatch.setattr(m_platform, "system", patch)

        assert FileNameSanitizer(255, platform="auto").platform == expected

    @pytest.mark.parametrize(
        ["test_platform", "expected"],
        [
            [
                "windows",
                (
                    ".",
                    "..",
                    "CON",
                    "PRN",
                    "AUX",
                    "NUL",
                    "COM1",
                    "COM2",
                    "COM3",
                    "COM4",
                    "COM5",
                    "COM6",
                    "COM7",
                    "COM8",
                    "COM9",
                    "LPT1",
                    "LPT2",
                    "LPT3",
                    "LPT4",
                    "LPT5",
                    "LPT6",
                    "LPT7",
                    "LPT8",
                    "LPT9",
                ),
            ],
            ["linux", (".", "..")],
            ["macos", (".", "..")],
        ],
    )
    def test_normal_reserved_keywords(self, test_platform, expected):
        assert FileNameSanitizer(255, platform=test_platform).reserved_keywords == expected


class Test_validate_filename(object):
    VALID_CHARS = VALID_FILENAME_CHARS
    INVALID_CHARS = INVALID_WIN_FILENAME_CHARS + unprintable_ascii_chars

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [
                    arg_list
                    for arg_list in product(
                        [make_random_str(64) + valid_char + make_random_str(64)],
                        VALID_PLATFORM_NAMES,
                    )
                ]
                for valid_char in VALID_CHARS
            ]
        ),
    )
    def test_normal(self, value, platform):
        validate_filename(value, platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [arg_list for arg_list in product([multibyte_name], VALID_PLATFORM_NAMES)]
                for multibyte_name in VALID_MULTIBYTE_NAMES
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform):
        validate_filename(value, platform)

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["a" * 255, None, None, None],
            ["a" * 5000, None, 10000, InvalidLengthError],
            ["invalid_max_len", None, 0, ValueError],
            ["valid_length", "universal", 255, None],
            ["valid_length", Platform.UNIVERSAL, 255, None],
            ["invalid_length", None, 2, InvalidLengthError],
        ],
    )
    def test_max_len(self, value, platform, max_len, expected):
        if expected is None:
            validate_filename(value, platform=platform, max_len=max_len)
        else:
            with pytest.raises(expected):
                validate_filename(value, platform=platform, max_len=max_len)

    @pytest.mark.parametrize(["locale"], [[None], ["ja_JP"]])
    def test_locale_ja(self, locale):
        fake = Factory.create(locale=locale, seed=1)

        for _ in range(100):
            validate_filename(fake.file_name())

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [
                    arg_list
                    for arg_list in product(
                        [make_random_str(64) + invalid_c + make_random_str(64)],
                        VALID_PLATFORM_NAMES,
                    )
                ]
                for invalid_c in INVALID_FILENAME_CHARS
            ]
        ),
    )
    def test_exception_invalid_char(self, value, platform):
        with pytest.raises(InvalidCharError):
            validate_filename(value, platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            [make_random_str(64) + invalid_c + make_random_str(64), platform]
            for invalid_c, platform in product(
                set(INVALID_WIN_PATH_CHARS).difference(
                    set(INVALID_PATH_CHARS + INVALID_FILENAME_CHARS + unprintable_ascii_chars)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_win_invalid_char(self, value, platform):
        with pytest.raises(InvalidCharError):
            validate_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform", "expected"],
        [
            [reserved_keyword, platform, ReservedNameError]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
        ]
        + [
            [reserved_keyword, platform, ReservedNameError]
            for reserved_keyword, platform in product([".", ".."], ["linux", "macos"])
        ],
    )
    def test_exception_reserved_name(self, value, platform, expected):
        with pytest.raises(expected) as e:
            validate_filename(value, platform=platform)
        assert e.value.reusable_name is False

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [None, ValueError],
            ["", NullNameError],
            ["a" * 256, InvalidLengthError],
            [1, TypeError],
            [True, TypeError],
            [nan, TypeError],
            [inf, TypeError],
        ],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filename(value)


class Test_sanitize_filename(object):
    SANITIZE_CHARS = INVALID_WIN_FILENAME_CHARS + unprintable_ascii_chars
    NOT_SANITIZE_CHARS = VALID_FILENAME_CHARS
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["platform", "value", "replace_text", "expected"],
        [
            ["universal", "A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(
                INVALID_WIN_FILENAME_CHARS + unprintable_ascii_chars, REPLACE_TEXT_LIST
            )
        ]
        + [
            ["universal", "A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            ["linux", "A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(
                INVALID_FILENAME_CHARS + unprintable_ascii_chars, REPLACE_TEXT_LIST
            )
        ]
        + [
            ["linux", "A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product([":", "*", "?", '"', "<", ">", "|"], REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_str(self, platform, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, platform=platform, replacement_text=replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, six.text_type)
        validate_filename(sanitized_name, platform=platform)

    @pytest.mark.skipif("sys.version_info[0:2] <= (3, 5)")
    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [Path("A" + c + "B"), rep, Path("A" + rep + "B")]
            for c, rep in product(SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            [Path("A" + c + "B"), rep, Path("A" + c + "B")]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_pathlike(self, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, replace_text)
        assert sanitized_name == expected
        assert is_pathlike_obj(sanitized_name)

        validate_filename(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [["あい/うえお.txt", "", "あいうえお.txt"], ["属/性.txt", "-", "属-性.txt"]],
    )
    def test_normal_multibyte(self, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, replace_text)
        assert sanitized_name == expected
        validate_filename(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "max_len", "expected"],
        [["a" * 10, 255, 10], ["invalid_length" * 100, 255, 255], ["invalid_length" * 100, 10, 10]],
    )
    def test_normal_max_len(self, value, max_len, expected):
        assert len(sanitize_filename(value, max_len=max_len)) == expected

    @pytest.mark.parametrize(
        ["value", "test_platform", "expected"],
        [
            [reserved.lower(), "windows", reserved.lower() + "_"]
            for reserved in WIN_RESERVED_FILE_NAMES
        ]
        + [
            [reserved.upper(), "windows", reserved.upper() + "_"]
            for reserved in WIN_RESERVED_FILE_NAMES
        ]
        + [[reserved, "linux", reserved + "_"] for reserved in (".", "..")],
    )
    def test_normal_reserved_name(self, monkeypatch, value, test_platform, expected):
        assert sanitize_filename(value, platform=test_platform) == expected

    @pytest.mark.parametrize(
        ["platform", "value", "expected"],
        [
            ["windows", "period.", "period"],
            ["windows", "space ", "space"],
            ["windows", "space_and_period .", "space_and_period"],
            ["windows", "space_and_period. ", "space_and_period"],
            ["linux", "period.", "period."],
            ["linux", "space ", "space "],
            ["linux", "space_and_period. ", "space_and_period. "],
            ["universal", "period.", "period"],
            ["universal", "space ", "space"],
            ["universal", "space_and_period .", "space_and_period"],
        ],
    )
    def test_normal_space_or_period_at_tail(self, monkeypatch, platform, value, expected):
        assert sanitize_filename(value, platform=platform) == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [[None, ValueError], [1, TypeError], [True, TypeError]]
    )
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filename(value)
