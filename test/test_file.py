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
from pathvalidate import (
    InvalidCharError,
    InvalidLengthError,
    NullNameError,
    Platform,
    ReservedNameError,
    sanitize_filename,
    sanitize_filepath,
    validate_filename,
    validate_filepath,
)
from pathvalidate._common import is_pathlike_obj, unprintable_ascii_char_list
from pathvalidate._file import FileNameSanitizer

from ._common import (
    INVALID_FILENAME_CHARS,
    INVALID_PATH_CHARS,
    INVALID_WIN_FILENAME_CHARS,
    INVALID_WIN_PATH_CHARS,
    VALID_FILENAME_CHARS,
    VALID_PATH_CHARS,
    make_random_str,
)


try:
    from pathlib import Path
except ImportError:
    Path = six.text_type


nan = float("nan")
inf = float("inf")

random.seed(0)

VALID_PLATFORM_NAME_LIST = ["universal", "linux", "windows", "macos"]

WIN_RESERVED_FILE_NAME_LIST = [
    ".",
    "..",
    "CON",
    "con",
    "PRN",
    "prn",
    "AUX",
    "aux",
    "NUL",
    "nul",
] + [
    "{:s}{:d}".format(name, num)
    for name, num in product(["COM", "com", "LPT", "lpt"], range(1, 10))
]

VALID_MULTIBYTE_NAME_LIST = ["新しいテキスト ドキュメント.txt", "新規 Microsoft Excel Worksheet.xlsx"]


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

        assert FileNameSanitizer("value", 255, platform_name="auto").platform_name == expected

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
    def test_normal_reserved_keywords(self, monkeypatch, test_platform, expected):
        assert (
            FileNameSanitizer("v", 255, platform_name=test_platform).reserved_keywords == expected
        )


class Test_validate_filename(object):
    VALID_CHAR_LIST = VALID_FILENAME_CHARS
    INVALID_CHAR_LIST = INVALID_WIN_FILENAME_CHARS + unprintable_ascii_char_list

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        chain.from_iterable(
            [
                [
                    arg_list
                    for arg_list in product(
                        [make_random_str(64) + valid_char + make_random_str(64)],
                        VALID_PLATFORM_NAME_LIST,
                    )
                ]
                for valid_char in VALID_CHAR_LIST
            ]
        ),
    )
    def test_normal(self, value, platform_name):
        validate_filename(value, platform_name)

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        chain.from_iterable(
            [
                [arg_list for arg_list in product([multibyte_name], VALID_PLATFORM_NAME_LIST)]
                for multibyte_name in VALID_MULTIBYTE_NAME_LIST
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform_name):
        validate_filename(value, platform_name)

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["a" * 255, None, None, None],
            ["a" * 5000, None, 10000, InvalidLengthError],
            ["valid_length", "universal", 255, None],
            ["valid_length", Platform.UNIVERSAL, 255, None],
            ["invalid_length", None, 2, InvalidLengthError],
        ],
    )
    def test_normal_max_filename_len(self, value, platform, max_len, expected):
        if expected is None:
            validate_filename(value, platform_name=platform, max_filename_len=max_len)
        else:
            with pytest.raises(expected):
                validate_filename(value, platform_name=platform, max_filename_len=max_len)

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        chain.from_iterable(
            [
                [
                    arg_list
                    for arg_list in product(
                        [make_random_str(64) + invalid_c + make_random_str(64)],
                        VALID_PLATFORM_NAME_LIST,
                    )
                ]
                for invalid_c in INVALID_FILENAME_CHARS
            ]
        ),
    )
    def test_exception_invalid_char(self, value, platform_name):
        with pytest.raises(InvalidCharError):
            validate_filename(value, platform_name)

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        [
            [make_random_str(64) + invalid_c + make_random_str(64), platform_name]
            for invalid_c, platform_name in product(
                set(INVALID_WIN_PATH_CHARS).difference(
                    set(INVALID_PATH_CHARS + INVALID_FILENAME_CHARS + unprintable_ascii_char_list)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_win_invalid_char(self, value, platform_name):
        with pytest.raises(InvalidCharError):
            validate_filename(value, platform_name=platform_name)

    @pytest.mark.parametrize(
        ["value", "platform_name", "expected"],
        [
            [reserved_keyword, platform_name, ReservedNameError]
            for reserved_keyword, platform_name in product(
                WIN_RESERVED_FILE_NAME_LIST, ["windows", "universal"]
            )
        ]
        + [
            [reserved_keyword, platform_name, ReservedNameError]
            for reserved_keyword, platform_name in product([".", ".."], ["linux", "macos"])
        ],
    )
    def test_exception_reserved_name(self, value, platform_name, expected):
        with pytest.raises(expected) as e:
            validate_filename(value, platform_name=platform_name)
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


class Test_validate_filepath(object):
    VALID_CHAR_LIST = VALID_PATH_CHARS
    VALID_MULTIBYTE_PATH_LIST = [
        r"\\localhost\Users\新しいフォルダー\あいうえお.txt",
        r"\\localhost\新しいフォルダー\ユーザ属性.txt",
    ]
    WIN_VALID_PATH_LIST = [
        r"\\\localhost\Users\test\AppData\Local\Temp\pytest-of-test\pytest-0\test_exception__hoge_csv_heade1\hoge.csv",
        r"\\localhost/Users/test/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv",
        r"\\localhost\Users\test\AppData/Local\Temp/pytest-of-test\pytest-0/test_exception__hoge_csv_heade1\hoge.csv",
        r"\\localhost\Users",
        "\\\\localhost\\",
        r"\Users",
    ]

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        chain.from_iterable(
            [
                [
                    arg_list
                    for arg_list in product(
                        [make_random_str(64) + valid_char + make_random_str(64)],
                        VALID_PLATFORM_NAME_LIST,
                    )
                ]
                for valid_char in VALID_CHAR_LIST
            ]
        ),
    )
    def test_normal(self, value, platform_name):
        validate_filepath(value, platform_name)

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        chain.from_iterable(
            [
                [arg_list for arg_list in product([valid_path], VALID_PLATFORM_NAME_LIST)]
                for valid_path in VALID_MULTIBYTE_PATH_LIST
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform_name):
        validate_filepath(value, platform_name)

    @pytest.mark.parametrize(["value"], [[valid_path] for valid_path in WIN_VALID_PATH_LIST])
    def test_normal_win(self, value):
        validate_filepath(value, "windows")

    @pytest.mark.parametrize(
        ["value", "platform_name", "max_path_len", "expected"],
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
    def test_normal_max_path_len(self, value, platform_name, max_path_len, expected):
        if expected is None:
            validate_filepath(value, platform_name=platform_name, max_path_len=max_path_len)
        else:
            with pytest.raises(expected):
                validate_filepath(value, platform_name=platform_name, max_path_len=max_path_len)

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

    @pytest.mark.parametrize(
        ["value", "platform_name"],
        [
            ["{}_{}_{}".format(make_random_str(64), invalid_c, make_random_str(64)), platform_name]
            for invalid_c, platform_name in product(
                set(INVALID_WIN_PATH_CHARS + unprintable_ascii_char_list).difference(
                    set(INVALID_PATH_CHARS)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_invalid_win_char(self, value, platform_name):
        with pytest.raises(InvalidCharError):
            validate_filepath(value, platform_name=platform_name)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[None, ValueError], ["", NullNameError], [1, TypeError], [True, TypeError]],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filepath(value)


@pytest.mark.skipif("m_platform.system() != 'Windows'")
class Test_validate_win_file_path(object):
    VALID_CHAR_LIST = VALID_PATH_CHARS

    @pytest.mark.parametrize(
        ["value"],
        [
            [
                r"C:\Users\test\AppData\Local\Temp\pytest-of-test\pytest-0\test_exception__hoge_csv_heade1\hoge.csv"
            ],
            [
                r"Z:\Users\test\AppData\Local\Temp\pytest-of-test\pytest-0\test_exception__hoge_csv_heade1\hoge.csv"
            ],
            [
                r"C:/Users/test/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv"
            ],
            [
                r"C:\Users/test\AppData/Local\Temp/pytest-of-test\pytest-0/test_exception__hoge_csv_heade1\hoge.csv"
            ],
            [r"C:\Users"],
            ["C:\\"],
            [r"\Users"],
        ],
    )
    def test_normal(self, value):
        validate_filepath(value)


class Test_sanitize_filename(object):
    SANITIZE_CHAR_LIST = INVALID_WIN_FILENAME_CHARS + unprintable_ascii_char_list
    NOT_SANITIZE_CHAR_LIST = VALID_FILENAME_CHARS
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_str(self, value, replace_text, expected):
        sanitized_name = sanitize_filename(value, replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, six.text_type)
        validate_filename(sanitized_name)

    @pytest.mark.skipif("sys.version_info[0:2] <= (3, 5)")
    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [Path("A" + c + "B"), rep, Path("A" + rep + "B")]
            for c, rep in product(SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            [Path("A" + c + "B"), rep, Path("A" + c + "B")]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
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
        ["value", "max_filename_len", "expected"],
        [["a" * 10, 255, 10], ["invalid_length" * 100, 255, 255], ["invalid_length" * 100, 10, 10]],
    )
    def test_normal_max_filename_len(self, value, max_filename_len, expected):
        assert len(sanitize_filename(value, max_filename_len=max_filename_len)) == expected

    @property
    def platform_win(self):
        return "windows"

    @property
    def platform_linux(self):
        return "linux"

    @pytest.mark.parametrize(
        ["value", "test_platform", "expected"],
        [
            [reserved.lower(), "windows", reserved.lower() + "_"]
            for reserved in WIN_RESERVED_FILE_NAME_LIST
        ]
        + [
            [reserved.upper(), "windows", reserved.upper() + "_"]
            for reserved in WIN_RESERVED_FILE_NAME_LIST
        ]
        + [[reserved, "linux", reserved + "_"] for reserved in (".", "..")],
    )
    def test_normal_reserved_name(self, monkeypatch, value, test_platform, expected):
        assert sanitize_filename(value, platform_name=test_platform) == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [[None, ValueError], [1, TypeError], [True, TypeError]]
    )
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filename(value)


class Test_sanitize_filepath(object):
    SANITIZE_CHAR_LIST = INVALID_WIN_PATH_CHARS + unprintable_ascii_char_list
    NOT_SANITIZE_CHAR_LIST = VALID_PATH_CHARS
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in product(SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            ["あ" + c + "い", rep, "あ" + c + "い"]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_str(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, six.text_type)
        validate_filepath(sanitized_name)

    @pytest.mark.skipif("sys.version_info[0:2] <= (3, 5)")
    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [Path("A" + c + "B"), rep, Path("A" + rep + "B")]
            for c, rep in product(SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            [Path("A" + c + "B"), rep, Path("A" + c + "B")]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
        + [
            [Path("あ" + c + "い"), rep, Path("あ" + c + "い")]
            for c, rep in product(NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ],
    )
    def test_normal_pathlike(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        assert is_pathlike_obj(sanitized_name)

        validate_filepath(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [["/tmp/あいう\0えお.txt", "", "/tmp/あいうえお.txt"], ["/tmp/属\0性.txt", "-", "/tmp/属-性.txt"]],
    )
    def test_normal_multibyte(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        validate_filepath(sanitized_name)

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[None, ValueError], [1, TypeError], [True, TypeError], [nan, TypeError], [inf, TypeError]],
    )
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filepath(value)
