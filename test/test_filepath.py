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
    is_valid_filepath,
    sanitize_filepath,
    validate_filepath,
)
from pathvalidate._common import is_pathlike_obj, unprintable_ascii_chars
from pathvalidate._file import FileNameSanitizer

from ._common import (
    INVALID_PATH_CHARS,
    INVALID_WIN_PATH_CHARS,
    VALID_PATH_CHARS,
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


class Test_validate_filepath(object):
    VALID_CHARS = VALID_PATH_CHARS
    VALID_MULTIBYTE_PATH_LIST = [
        "\\\\localhost\\Users\\新しいフォルダー\\あいうえお.txt",
        "\\\\localhost\\新しいフォルダー\\ユーザ属性.txt",
    ]
    WIN_VALID_PATH_LIST = [
        "\\\\localhost\\Users\\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\\hoge.csv",
        "\\\\localhost/Users/test/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv",
        "\\\\localhost\\Users\\est\\AppData/Local\\Temp/pytest-of-test\\pytest-0/\hoge.csv",
        "\\\\localhost\\Users",
        "\\\\localhost\\",
        "\\Users",
    ]

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
        validate_filepath(value, platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [arg_list for arg_list in product([valid_path], VALID_PLATFORM_NAMES)]
                for valid_path in VALID_MULTIBYTE_PATH_LIST
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform):
        validate_filepath(value, platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(["value"], [[valid_path] for valid_path in WIN_VALID_PATH_LIST])
    def test_normal_win(self, value):
        platform = "windows"
        validate_filepath(value, platform=platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "min_len", "expected"],
        [
            ["lower than one", -1, None],
            ["valid", 5, None],
            ["invalid_length", 200, InvalidLengthError],
        ],
    )
    def test_normal_min_len(self, value, min_len, expected):
        if expected is None:
            validate_filepath(value, min_len=min_len)
            assert is_valid_filepath(value, min_len=min_len)
        else:
            with pytest.raises(expected):
                validate_filepath(value, min_len=min_len)

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["a" * 4096, "linux", None, None],
            ["a" * 4097, "linux", None, InvalidLengthError],
            ["a" * 4097, Platform.LINUX, None, InvalidLengthError],
            ["a" * 255, "linux", 100, InvalidLengthError],
            ["a" * 260, "windows", None, None],
            ["a" * 261, Platform.WINDOWS, None, InvalidLengthError],
            ["a" * 261, "windows", None, InvalidLengthError],
            ["a" * 260, "universal", None, None],
            ["a" * 261, "universal", None, InvalidLengthError],
            ["a" * 261, Platform.UNIVERSAL, None, InvalidLengthError],
        ],
    )
    def test_normal_max_len(self, value, platform, max_len, expected):
        if expected is None:
            validate_filepath(value, platform=platform, max_len=max_len)
            assert is_valid_filepath(value, platform=platform, max_len=max_len)
        else:
            with pytest.raises(expected):
                validate_filepath(value, platform=platform, max_len=max_len)

    @pytest.mark.parametrize(
        ["value", "min_len", "max_len", "expected"],
        [
            ["valid length", 1, 255, None],
            ["eq min max", 10, 10, None],
            ["inversion", 100, 1, ValueError],
        ],
    )
    def test_minmax_len(self, value, min_len, max_len, expected):
        if expected is None:
            validate_filepath(value, min_len=min_len, max_len=max_len)
            assert is_valid_filepath(value, min_len=min_len, max_len=max_len)
        else:
            with pytest.raises(expected):
                validate_filepath(value, min_len=min_len, max_len=max_len)

    @pytest.mark.parametrize(
        ["platform", "value"],
        [
            ["windows", "period."],
            ["windows", "space "],
            ["windows", "space_and_period ."],
            ["windows", "space_and_period. "],
            ["linux", "period."],
            ["linux", "space "],
            ["linux", "space_and_period. "],
            ["universal", "period."],
            ["universal", "space "],
            ["universal", "space_and_period ."],
        ],
    )
    def test_normal_space_or_period_at_tail(self, monkeypatch, platform, value):
        validate_filepath(value, platform=platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(["locale"], [[None], ["ja_JP"]])
    def test_locale_jp(self, locale):
        fake = Factory.create(locale=locale, seed=1)

        for _ in range(100):
            filepath = fake.file_path()
            validate_filepath(filepath)
            assert is_valid_filepath(filepath)

    @pytest.mark.parametrize(
        ["value"],
        [
            [make_random_str(64) + invalid_c + make_random_str(64)]
            for invalid_c in INVALID_PATH_CHARS
        ],
    )
    def test_exception_invalid_char(self, value):
        with pytest.raises(InvalidCharError):
            validate_filepath(value)
        assert not is_valid_filepath(value)

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            ["{}_{}_{}".format(make_random_str(64), invalid_c, make_random_str(64)), platform]
            for invalid_c, platform in product(
                set(INVALID_WIN_PATH_CHARS + unprintable_ascii_chars).difference(
                    set(INVALID_PATH_CHARS)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_invalid_win_char(self, value, platform):
        with pytest.raises(InvalidCharError):
            validate_filepath(value, platform=platform)
        assert not is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[None, ValueError], ["", NullNameError], [1, TypeError], [True, TypeError]],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filepath(value)
        assert not is_valid_filepath(value)


@pytest.mark.skipif("m_platform.system() != 'Windows'")
class Test_validate_win_file_path(object):
    VALID_CHARS = VALID_PATH_CHARS

    @pytest.mark.parametrize(
        ["value"],
        [
            ["C:\\Users\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\\hoge.csv"],
            ["Z:\\Users\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\hoge.csv"],
            [
                "C:/Users/est/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv"
            ],
            ["C:\\Users/est\\AppData/Local\\Temp/pytest-of-test\\pytest-0/hoge.csv"],
            ["C:\\Users"],
            ["C:\\"],
            ["\\Users"],
        ],
    )
    def test_normal(self, value):
        validate_filepath(value)
        assert is_valid_filepath(value)


class Test_sanitize_filepath(object):
    SANITIZE_CHARS = INVALID_WIN_PATH_CHARS + unprintable_ascii_chars
    NOT_SANITIZE_CHARS = VALID_PATH_CHARS
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["platform", "value", "replace_text", "expected"],
        [
            ["universal", "A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            ["universal", "A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            ["universal", "あ" + c + "い", rep, "あ" + c + "い"]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ]
        + [
            ["linux", "A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(INVALID_PATH_CHARS + unprintable_ascii_chars, REPLACE_TEXT_LIST)
        ]
        + [
            ["linux", "A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product([":", "*", "?", '"', "<", ">", "|"], REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_str(self, platform, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, platform=platform, replacement_text=replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, six.text_type)
        validate_filepath(sanitized_name, platform=platform)
        assert is_valid_filepath(sanitized_name, platform=platform)

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
        ]
        + [
            [Path("あ" + c + "い"), rep, Path("あ" + c + "い")]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_pathlike(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        assert is_pathlike_obj(sanitized_name)

        validate_filepath(sanitized_name)
        assert is_valid_filepath(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [["/tmp/あいう\0えお.txt", "", "/tmp/あいうえお.txt"], ["/tmp/属\0性.txt", "-", "/tmp/属-性.txt"]],
    )
    def test_normal_multibyte(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        validate_filepath(sanitized_name)
        assert is_valid_filepath(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[None, ValueError], [1, TypeError], [True, TypeError], [nan, TypeError], [inf, TypeError]],
    )
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filepath(value)
        assert not is_valid_filepath(value)
