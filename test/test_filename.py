"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import platform as m_platform
import random
from collections import OrderedDict
from itertools import chain, product
from pathlib import Path

import pytest
from allpairspy import AllPairs

from pathvalidate import (
    ErrorReason,
    Platform,
    ValidationError,
    is_valid_filename,
    sanitize_filename,
    validate_filename,
)
from pathvalidate._common import is_pathlike_obj, unprintable_ascii_chars
from pathvalidate._filename import FileNameSanitizer, FileNameValidator

from ._common import (
    INVALID_FILENAME_CHARS,
    INVALID_PATH_CHARS,
    INVALID_WIN_FILENAME_CHARS,
    INVALID_WIN_PATH_CHARS,
    NTFS_RESERVED_FILE_NAMES,
    VALID_FILENAME_CHARS,
    VALID_PLATFORM_NAMES,
    WIN_RESERVED_FILE_NAMES,
    is_faker_installed,
    randstr,
)


nan = float("nan")
inf = float("inf")

random.seed(0)

VALID_MULTIBYTE_NAMES = ["新しいテキスト ドキュメント.txt", "新規 Microsoft Excel Worksheet.xlsx"]


class Test_FileSanitizer:
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
                    "CON",
                    "PRN",
                    "AUX",
                    "CLOCK$",
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
            ["linux", ()],
            ["macos", (":",)],
        ],
    )
    def test_normal_reserved_keywords(self, test_platform, expected):
        assert FileNameValidator(255, platform=test_platform).reserved_keywords == expected


class Test_validate_filename:
    VALID_CHARS = VALID_FILENAME_CHARS
    INVALID_CHARS = INVALID_WIN_FILENAME_CHARS + unprintable_ascii_chars

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [
                    args
                    for args in product(
                        ["{0}{1}{0}".format(randstr(64), valid_c)], VALID_PLATFORM_NAMES
                    )
                ]
                for valid_c in VALID_CHARS
            ]
            + [
                [args for args in product([filename], VALID_PLATFORM_NAMES)]
                for filename in NTFS_RESERVED_FILE_NAMES
            ]
        ),
    )
    def test_normal(self, value, platform):
        validate_filename(value, platform)
        assert is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["platform"],
        [["linux"], ["macos"], ["posix"]],
    )
    def test_normal_only_whitespaces(self, platform):
        value = "  "
        validate_filename(value, platform)
        assert is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["platform"],
        [["windows"], ["universal"]],
    )
    def test_abnormal_only_whitespaces(self, platform):
        value = "  "
        with pytest.raises(ValidationError) as e:
            validate_filename(value, platform=platform)
            assert e.value.reason == ErrorReason.NULL
        assert not is_valid_filename(value, platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [args for args in product([multibyte_name], VALID_PLATFORM_NAMES)]
                for multibyte_name in VALID_MULTIBYTE_NAMES
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform):
        validate_filename(value, platform)
        assert is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "min_len", "expected"],
        [
            ["lower than one", -1, None],
            ["valid", 5, None],
            ["invalid_length", 200, ErrorReason.INVALID_LENGTH],
        ],
    )
    def test_min_len(self, value, min_len, expected):
        if expected is None:
            validate_filename(value, min_len=min_len)
            assert is_valid_filename(value, min_len=min_len)
        else:
            with pytest.raises(ValidationError) as e:
                validate_filename(value, min_len=min_len)
            assert e.value.reason == expected

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["a" * 255, None, None, None],
            ["a" * 5000, None, 10000, ErrorReason.INVALID_LENGTH],
            ["valid_length", "universal", 255, None],
            ["valid_length", Platform.UNIVERSAL, 255, None],
            ["invalid_length", None, 2, ErrorReason.INVALID_LENGTH],
        ],
    )
    def test_max_len(self, value, platform, max_len, expected):
        if expected is None:
            validate_filename(value, platform=platform, max_len=max_len)
            assert is_valid_filename(value, platform=platform, max_len=max_len)
            return

        with pytest.raises(ValidationError) as e:
            validate_filename(value, platform=platform, max_len=max_len)
        assert e.value.reason == expected

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["invalid_max_len", None, 0, ValueError],
        ],
    )
    def test_abnormal_max_len(self, value, platform, max_len, expected):
        with pytest.raises(expected):
            validate_filename(value, platform=platform, max_len=max_len)

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
            validate_filename(value, min_len=min_len, max_len=max_len)
            assert is_valid_filename(value, min_len=min_len, max_len=max_len)
        else:
            with pytest.raises(expected):
                validate_filename(value, min_len=min_len, max_len=max_len)

    @pytest.mark.skipif(not is_faker_installed(), reason="requires faker")
    @pytest.mark.parametrize(["locale"], [[None], ["ja_JP"]])
    def test_locale_ja(self, locale):
        from faker import Factory

        fake = Factory.create(locale=locale, seed=1)

        for _ in range(100):
            filename = fake.file_name()
            validate_filename(filename)
            assert is_valid_filename(filename)

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [
                    args
                    for args in product(
                        ["{0}{1}{0}".format(randstr(64), invalid_c)], VALID_PLATFORM_NAMES
                    )
                ]
                for invalid_c in INVALID_FILENAME_CHARS
            ]
        ),
    )
    def test_exception_invalid_char(self, value, platform):
        with pytest.raises(ValidationError) as e:
            validate_filename(value, platform)
        assert e.value.reason == ErrorReason.INVALID_CHARACTER
        assert not is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            ["{0}{1}{0}".format(randstr(64), invalid_c), platform]
            for invalid_c, platform in product(
                set(INVALID_WIN_PATH_CHARS).difference(
                    set(INVALID_PATH_CHARS + INVALID_FILENAME_CHARS + unprintable_ascii_chars)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_win_invalid_char(self, value, platform):
        with pytest.raises(ValidationError) as e:
            validate_filename(value, platform=platform)
        assert e.value.reason == ErrorReason.INVALID_CHARACTER
        assert not is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform", "expected"],
        [
            [reserved_keyword, platform, ValidationError]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
        ]
        + [
            ["{}.txt".format(reserved_keyword), platform, ValidationError]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
        ]
        + [
            [reserved_keyword, platform, None]
            for reserved_keyword, platform in product([".", ".."], ["posix", "linux", "macos"])
        ]
        + [
            [":", "posix", ValidationError],
            [":", "macos", ValidationError],
        ],
    )
    def test_reserved_name(self, value, platform, expected):
        if expected is None:
            validate_filename(value, platform=platform)
        else:
            with pytest.raises(expected) as e:
                validate_filename(value, platform=platform)
            assert e.value.reason == ErrorReason.RESERVED_NAME
            assert e.value.reserved_name
            assert e.value.reusable_name is False

            assert not is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["platform", "value", "expected"],
        [
            [win_abspath, platform, None]
            for win_abspath, platform in product(
                ["linux", "macos", "posix"],
                ["\\", "\\\\", "\\ ", "C:\\", "c:\\", "\\xyz", "\\xyz "],
            )
        ]
        + [
            [win_abspath, platform, ValidationError]
            for win_abspath, platform in product(
                ["windows", "universal"], ["\\", "\\\\", "\\ ", "C:\\", "c:\\", "\\xyz", "\\xyz "]
            )
        ],
    )
    def test_win_abs_path(self, platform, value, expected):
        if expected is None:
            validate_filename(value, platform=platform)
        else:
            with pytest.raises(expected) as e:
                validate_filename(value, platform=platform)
            assert e.value.reason == ErrorReason.FOUND_ABS_PATH

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            [value, platform]
            for value, platform in product(
                ["a/b.txt", "/a/b.txt", "c:\\Users"], ["windows", "universal"]
            )
        ],
    )
    def test_exception_filepath(self, value, platform):
        with pytest.raises(ValidationError) as e:
            validate_filename(value, platform=platform)
        assert e.value.reason in [ErrorReason.FOUND_ABS_PATH, ErrorReason.INVALID_CHARACTER]
        assert not is_valid_filename(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform", "expected"],
        [
            [value, platform, ErrorReason.INVALID_CHARACTER]
            for value, platform in product(["asdf\rsdf"], ["windows", "universal"])
        ],
    )
    def test_exception_escape_err_msg(self, value, platform, expected):
        with pytest.raises(ValidationError) as e:
            print(platform, repr(value))
            validate_filename(value, platform=platform)

        assert e.value.reason == ErrorReason.INVALID_CHARACTER
        assert str(e.value) == (
            r"invalid char found: invalids=('\r'), value='asdf\rsdf', "
            "reason=INVALID_CHARACTER, target-platform=Windows"
        )  # noqa

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [None, ValueError],
            ["", ValidationError],
            ["a" * 256, ValidationError],
            [1, TypeError],
            [True, TypeError],
            [nan, TypeError],
            [inf, TypeError],
        ],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filename(value)
        assert not is_valid_filename(value)


class Test_sanitize_filename:
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
            [pair.platform, "A" + pair.c + "B", pair.repl, "A" + pair.repl + "B"]
            for pair in AllPairs(
                OrderedDict(
                    {
                        "platform": ["posix", "linux", "macos"],
                        "c": INVALID_PATH_CHARS + unprintable_ascii_chars,
                        "repl": REPLACE_TEXT_LIST,
                    }
                )
            )
        ]
        + [
            [pair.platform, "A" + pair.c + "B", pair.repl, "A" + pair.c + "B"]
            for pair in AllPairs(
                OrderedDict(
                    {
                        "platform": ["posix", "linux", "macos"],
                        "c": [":", "*", "?", '"', "<", ">", "|"],
                        "repl": REPLACE_TEXT_LIST,
                    }
                )
            )
        ],
    )
    def test_normal_str(self, platform, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, platform=platform, replacement_text=replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, str)
        validate_filename(sanitized_name, platform=platform)
        assert is_valid_filename(sanitized_name, platform=platform)

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
        assert is_valid_filename(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["", ""],
            [None, ""],
        ],
    )
    def test_normal_null_values(self, value, expected):
        assert sanitize_filename(value) == expected

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [["あい/うえお.txt", "", "あいうえお.txt"], ["属/性.txt", "-", "属-性.txt"]],
    )
    def test_normal_multibyte(self, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, replace_text)
        assert sanitized_name == expected
        validate_filename(sanitized_name)
        assert is_valid_filename(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "max_len", "expected"],
        [["a" * 10, 255, 10], ["invalid_length" * 100, 255, 255], ["invalid_length" * 100, 10, 10]],
    )
    def test_normal_max_len(self, value, max_len, expected):
        filename = sanitize_filename(value, max_len=max_len)
        assert len(filename) == expected
        assert is_valid_filename(filename, max_len=max_len)

    @pytest.mark.parametrize(
        ["value", "test_platform", "expected"],
        [
            [reserved.lower(), "windows", reserved.lower() + "_"]
            for reserved in WIN_RESERVED_FILE_NAMES
        ]
        + [
            ["{}.txt".format(reserved_keyword), platform, "{}_.txt".format(reserved_keyword)]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
            if reserved_keyword not in [".", ".."]
        ]
        + [
            [reserved.upper(), "windows", reserved.upper() + "_"]
            for reserved in WIN_RESERVED_FILE_NAMES
        ]
        + [
            [reserved_keyword, platform, reserved_keyword]
            for reserved_keyword, platform in product([".", ".."], ["windows", "universal"])
        ],
    )
    def test_normal_reserved_name(self, value, test_platform, expected):
        filename = sanitize_filename(value, platform=test_platform)
        assert filename == expected
        assert is_valid_filename(filename, platform=test_platform)

    @pytest.mark.parametrize(
        ["value", "check_reserved", "expected"],
        [
            ["CON", True, "CON_"],
            ["CON", False, "CON"],
        ],
    )
    def test_normal_check_reserved(self, value, check_reserved, expected):
        assert (
            sanitize_filename(value, platform="windows", check_reserved=check_reserved) == expected
        )

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
    def test_normal_space_or_period_at_tail(self, platform, value, expected):
        filename = sanitize_filename(value, platform=platform)
        assert filename == expected
        assert is_valid_filename(filename, platform=platform)

    @pytest.mark.parametrize(["value", "expected"], [[1, TypeError], [True, TypeError]])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filename(value)
        assert not is_valid_filename(value)
