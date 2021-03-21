"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import platform as m_platform
import random
import sys
from collections import OrderedDict
from itertools import chain, product
from pathlib import Path

import pytest
from allpairspy import AllPairs

from pathvalidate import (
    ErrorReason,
    Platform,
    ValidationError,
    is_valid_filepath,
    sanitize_filepath,
    validate_filepath,
)
from pathvalidate._common import is_pathlike_obj, unprintable_ascii_chars
from pathvalidate._filepath import FilePathSanitizer, FilePathValidator

from ._common import (
    INVALID_PATH_CHARS,
    INVALID_WIN_PATH_CHARS,
    NTFS_RESERVED_FILE_NAMES,
    VALID_PATH_CHARS,
    WIN_RESERVED_FILE_NAMES,
    is_faker_installed,
    randstr,
)


nan = float("nan")
inf = float("inf")

random.seed(0)


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

        assert FilePathSanitizer(255, platform="auto").platform == expected

    @pytest.mark.parametrize(
        ["test_platform", "expected"],
        [
            ["windows", tuple()],
            ["posix", ("/", ":")],
            ["linux", ("/",)],
            ["macos", ("/", ":")],
        ],
    )
    def test_normal_reserved_keywords(self, test_platform, expected):
        assert FilePathValidator(255, platform=test_platform).reserved_keywords == expected


class Test_validate_filepath:
    VALID_CHARS = VALID_PATH_CHARS
    VALID_MULTIBYTE_PATHS = [
        "c:\\Users\\新しいフォルダー\\あいうえお.txt",
        "D:\\新しいフォルダー\\ユーザ属性.txt",
    ]
    WIN_VALID_PATHS = [
        "D:\\Users\\\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\\\hoge.csv",
        "D:/Users/test/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv",  # noqa
        "C:\\Users\\est\\AppData/Local\\Temp/pytest-of-test\\pytest-0/\\hoge.csv",
        "C:\\Users",
        "C:\\",
        "\\Users",
    ]

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [
                    args
                    for args in product(
                        ["/{0}/{1}{0}".format(randstr(64), valid_c)], ["linux", "macos"]
                    )
                ]
                for valid_c in VALID_CHARS
            ]
        ),
    )
    def test_normal(self, value, platform):
        validate_filepath(value, platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["platform"],
        [["linux"], ["macos"], ["posix"]],
    )
    def test_normal_only_whitespaces(self, platform):
        value = "  "
        validate_filepath(value, platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["platform"],
        [["windows"], ["universal"]],
    )
    def test_abnormal_only_whitespaces(self, platform):
        value = "  "
        with pytest.raises(ValidationError) as e:
            validate_filepath(value, platform=platform)
            assert e.value.reason == ErrorReason.NULL
        assert not is_valid_filepath(value, platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        chain.from_iterable(
            [
                [args for args in product([valid_path], ["windows"])]
                for valid_path in VALID_MULTIBYTE_PATHS
            ]
        ),
    )
    def test_normal_multibyte(self, value, platform):
        validate_filepath(value, platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(["value"], [[valid_path] for valid_path in WIN_VALID_PATHS])
    def test_normal_win(self, value):
        platform = "windows"
        validate_filepath(value, platform=platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "min_len", "expected"],
        [
            ["lower than one", -1, None],
            ["valid", 5, None],
            ["invalid_length", 200, ErrorReason.INVALID_LENGTH],
        ],
    )
    def test_normal_min_len(self, value, min_len, expected):
        if expected is None:
            validate_filepath(value, min_len=min_len)
            assert is_valid_filepath(value, min_len=min_len)
            return

        with pytest.raises(ValidationError) as e:
            validate_filepath(value, min_len=min_len)
        assert e.value.reason == expected

    @pytest.mark.parametrize(
        ["value", "platform", "max_len", "expected"],
        [
            ["a" * 4096, "linux", None, None],
            ["a" * 4097, "linux", None, ErrorReason.INVALID_LENGTH],
            ["a" * 1024, "posix", None, None],
            ["a" * 1025, "posix", None, ErrorReason.INVALID_LENGTH],
            ["a" * 4097, Platform.LINUX, None, ErrorReason.INVALID_LENGTH],
            ["a" * 255, "linux", 100, ErrorReason.INVALID_LENGTH],
            ["a" * 5000, "windows", 10000, ErrorReason.INVALID_LENGTH],
            ["a" * 260, "windows", None, None],
            ["a" * 300, "windows", 1024, ErrorReason.INVALID_LENGTH],
            ["a" * 261, Platform.WINDOWS, None, ErrorReason.INVALID_LENGTH],
            ["a" * 261, "windows", None, ErrorReason.INVALID_LENGTH],
            ["a" * 260, "universal", None, None],
            ["a" * 261, "universal", None, ErrorReason.INVALID_LENGTH],
            ["a" * 300, "universal", 1024, ErrorReason.INVALID_LENGTH],
            ["a" * 261, Platform.UNIVERSAL, None, ErrorReason.INVALID_LENGTH],
        ],
    )
    def test_normal_max_len(self, value, platform, max_len, expected):
        if expected is None:
            validate_filepath(value, platform=platform, max_len=max_len)
            assert is_valid_filepath(value, platform=platform, max_len=max_len)
            return

        with pytest.raises(ValidationError) as e:
            validate_filepath(value, platform=platform, max_len=max_len)
        assert e.value.reason == ErrorReason.INVALID_LENGTH

    @pytest.mark.parametrize(
        ["value", "min_len", "max_len", "expected"],
        [
            ["valid length", 1, 255, None],
            ["minus min_len", -2, 100, None],
            ["minus max_len", -3, -2, ValueError],
            ["zero max_len", -2, 0, ValueError],
            ["eq min max", 10, 10, None],
            ["inversion", 100, 1, ValueError],
        ],
    )
    def test_minmax_len(self, value, min_len, max_len, expected):
        if expected is None:
            validate_filepath(value, min_len=min_len, max_len=max_len)
            assert is_valid_filepath(value, min_len=min_len, max_len=max_len)
            return

        with pytest.raises(expected):
            validate_filepath(value, min_len=min_len, max_len=max_len)

    @pytest.mark.parametrize(
        ["test_platform", "value", "expected"],
        [
            ["linux", "/a/b/c.txt", None],
            ["linux", "C:\\a\\b\\c.txt", ValidationError],
            ["windows", "/a/b/c.txt", None],
            ["windows", "C:\\a\\b\\c.txt", None],
            ["universal", "/a/b/c.txt", ValidationError],
            ["universal", "C:\\a\\b\\c.txt", ValidationError],
        ],
    )
    def test_abs_path(self, test_platform, value, expected):
        if expected is None:
            validate_filepath(value, platform=test_platform)
            assert is_valid_filepath(value, platform=test_platform)
            return

        with pytest.raises(expected):
            validate_filepath(value, platform=test_platform)

    @pytest.mark.skipif(m_platform.system() != "Windows", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["C:\\a\\b\\c.txt", None],
        ],
    )
    def test_auto_platform_win(self, value, expected):
        if expected is None:
            validate_filepath(value, platform="auto")
            assert is_valid_filepath(value, platform="auto")
            return

        with pytest.raises(expected):
            validate_filepath(value, platform="auto")

    @pytest.mark.skipif(m_platform.system() != "Linux", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["/a/b/c.txt", None],
            ["C:\\a\\b\\c.txt", ValidationError],
        ],
    )
    def test_auto_platform_linux(self, value, expected):
        if expected is None:
            validate_filepath(value, platform="auto")
            assert is_valid_filepath(value, platform="auto")
            return

        with pytest.raises(expected):
            validate_filepath(value, platform="auto")

    @pytest.mark.parametrize(
        ["test_platform", "value", "expected"],
        [
            ["linux", "a/b/c.txt", None],
            ["linux", "a//b?/c.txt", None],
            ["linux", "../a/./../b/c.txt", None],
            ["windows", "a/b/c.txt", None],
            ["windows", "a//b?/c.txt", ValidationError],
            ["windows", "../a/./../b/c.txt", None],
            ["universal", "a/b/c.txt", None],
            ["universal", "./a/b/c.txt", None],
            ["universal", "../a/./../b/c.txt", None],
            ["universal", "a//b?/c.txt", ValidationError],
        ],
    )
    def test_relative_path(self, test_platform, value, expected):
        if expected is None:
            validate_filepath(value, platform=test_platform)
            assert is_valid_filepath(value, platform=test_platform)
        else:
            with pytest.raises(expected):
                validate_filepath(value, platform=test_platform)

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
    def test_normal_space_or_period_at_tail(self, platform, value):
        validate_filepath(value, platform=platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.skipif(not is_faker_installed(), reason="requires faker")
    @pytest.mark.parametrize(["locale"], [[None], ["ja_JP"]])
    def test_locale_jp(self, locale):
        from faker import Factory

        fake = Factory.create(locale=locale, seed=1)

        for _ in range(100):
            filepath = fake.file_path()
            validate_filepath(filepath, platform="linux")
            assert is_valid_filepath(filepath, platform="linux")

    @pytest.mark.parametrize(
        ["value"],
        [["{0}{1}{0}".format(randstr(64), invalid_c)] for invalid_c in INVALID_PATH_CHARS],
    )
    def test_exception_invalid_char(self, value):
        with pytest.raises(ValidationError) as e:
            validate_filepath(value)
        assert e.value.reason == ErrorReason.INVALID_CHARACTER
        assert not is_valid_filepath(value)

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            ["{0}/{1}{0}".format(randstr(64), invalid_c), platform]
            for invalid_c, platform in product(
                set(INVALID_WIN_PATH_CHARS + unprintable_ascii_chars).difference(
                    set(INVALID_PATH_CHARS)
                ),
                ["windows", "universal"],
            )
        ],
    )
    def test_exception_invalid_win_char(self, value, platform):
        with pytest.raises(ValidationError) as e:
            validate_filepath(value, platform=platform)
        assert e.value.reason == ErrorReason.INVALID_CHARACTER
        assert not is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform"],
        [
            ["/foo/abc/{}.txt".format(reserved_keyword), platform]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["linux", "macos"])
            if reserved_keyword not in [".", ".."]
        ]
        + [
            ["{}\\{}_".format(drive, filename), platform]
            for drive, platform, filename in product(
                ["C:", "D:"], ["windows"], NTFS_RESERVED_FILE_NAMES
            )
        ]
        + [
            ["{}\\abc\\{}".format(drive, filename), platform]
            for drive, platform, filename in product(
                ["C:", "D:"], ["windows"], NTFS_RESERVED_FILE_NAMES
            )
        ],
    )
    def test_normal_reserved_name_used_valid_place(self, value, platform):
        validate_filepath(value, platform=platform)
        assert is_valid_filepath(value, platform=platform)

    @pytest.mark.parametrize(
        ["value", "platform", "expected"],
        [
            ["abc\\{}\\xyz".format(reserved_keyword), platform, ValidationError]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
            if reserved_keyword not in [".", ".."]
        ]
        + [
            ["foo/abc/{}.txt".format(reserved_keyword), platform, ValidationError]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["universal"])
            if reserved_keyword not in [".", ".."]
        ]
        + [
            ["{}".format(reserved_keyword), platform, ValidationError]
            for reserved_keyword, platform in product(
                WIN_RESERVED_FILE_NAMES, ["windows", "universal"]
            )
            if reserved_keyword not in [".", ".."]
        ]
        + [
            ["{}\\{}".format(drive, filename), platform, ValidationError]
            for drive, platform, filename in product(
                ["C:", "D:"], ["windows"], NTFS_RESERVED_FILE_NAMES
            )
        ],
    )
    def test_exception_reserved_name(self, value, platform, expected):
        with pytest.raises(expected) as e:
            print(platform, value)
            validate_filepath(value, platform=platform)
        assert e.value.reason == ErrorReason.RESERVED_NAME
        assert e.value.reusable_name is False
        assert e.value.reserved_name

        assert not is_valid_filepath(value, platform=platform)

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
            validate_filepath(value, platform=platform)

        assert e.value.reason == expected
        assert str(e.value) == (
            r"invalid char found: invalids=('\r'), value='asdf\rsdf', "
            "reason=INVALID_CHARACTER, target-platform=Windows"
        )  # noqa

    @pytest.mark.parametrize(
        ["value", "expected"],
        [[None, ValueError], ["", ValidationError], [1, TypeError], [True, TypeError]],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_filepath(value)
        assert not is_valid_filepath(value)


class Test_validate_win_file_path:
    VALID_CHARS = VALID_PATH_CHARS

    @pytest.mark.parametrize(
        ["value"],
        [
            ["C:\\Users\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\\\hoge.csv"],
            ["Z:\\Users\\est\\AppData\\Local\\Temp\\pytest-of-test\\pytest-0\\hoge.csv"],
            [
                "C:/Users/est/AppData/Local/Temp/pytest-of-test/pytest-0/test_exception__hoge_csv_heade1/hoge.csv"  # noqa
            ],
            ["C:\\Users/est\\AppData/Local\\Temp/pytest-of-test\\pytest-0/hoge.csv"],
            ["C:\\Users"],
            ["C:\\"],
            ["\\Users"],
        ],
    )
    def test_normal(self, value):
        validate_filepath(value, platform="windows")
        assert is_valid_filepath(value, platform="windows")

    @pytest.mark.parametrize(
        ["value", "platform", "expected"],
        [
            [r"C:\Users\a", "universal", ErrorReason.MALFORMED_ABS_PATH],
            [r"C:\Users:a", "universal", ErrorReason.MALFORMED_ABS_PATH],
            ["C:\\Users\\" + "a" * 1024, "windows", ErrorReason.INVALID_LENGTH],
            [r"C:\Users:a", "windows", ErrorReason.INVALID_CHARACTER],
        ],
    )
    def test_exception(self, value, platform, expected):
        with pytest.raises(ValidationError) as e:
            validate_filepath(value, platform=platform)
        assert e.value.reason == expected
        assert not is_valid_filepath(value, platform=platform)


class Test_sanitize_filepath:
    SANITIZE_CHARS = INVALID_WIN_PATH_CHARS + unprintable_ascii_chars
    NOT_SANITIZE_CHARS = VALID_PATH_CHARS
    REPLACE_TEXTS = ["", "_"]

    @pytest.mark.parametrize(
        ["platform", "value", "replace_text", "expected"],
        [
            ["universal", "AA" + c + "B", rep, "AA" + rep + "B"]
            for c, rep in product(SANITIZE_CHARS, REPLACE_TEXTS)
        ]
        + [
            ["universal", "A" + c + "B", rep, "A" + c + "B"]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXTS)
        ]
        + [
            ["universal", "あ" + c + "い", rep, "あ" + c + "い"]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXTS)
        ]
        + [
            [pair.platform, "A" + pair.c + "B", pair.repl, "A" + pair.repl + "B"]
            for pair in AllPairs(
                OrderedDict(
                    {
                        "platform": ["posix", "linux", "macos"],
                        "c": INVALID_PATH_CHARS + unprintable_ascii_chars,
                        "repl": REPLACE_TEXTS,
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
                        "repl": REPLACE_TEXTS,
                    }
                )
            )
        ],
    )
    def test_normal_str(self, platform, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, platform=platform, replacement_text=replace_text)
        assert sanitized_name == expected
        assert isinstance(sanitized_name, str)
        validate_filepath(sanitized_name, platform=platform)
        assert is_valid_filepath(sanitized_name, platform=platform)

    @pytest.mark.parametrize(
        ["value", "test_platform", "expected"],
        [
            [
                "abc/{}/xyz".format(reserved_keyword),
                platform,
                "abc/{}_/xyz".format(reserved_keyword),
            ]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["universal"])
        ]
        + [
            [
                "/abc/{}/xyz".format(reserved_keyword),
                platform,
                "/abc/{}/xyz".format(reserved_keyword),
            ]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["linux"])
        ]
        + [
            [
                "abc/{}.txt".format(reserved_keyword),
                platform,
                "abc/{}_.txt".format(reserved_keyword),
            ]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["universal"])
        ]
        + [
            [
                "/abc/{}.txt".format(reserved_keyword),
                platform,
                "/abc/{}.txt".format(reserved_keyword),
            ]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["linux"])
        ]
        + [
            [
                "C:\\abc\\{}.txt".format(reserved_keyword),
                platform,
                "C:\\abc\\{}_.txt".format(reserved_keyword),
            ]
            for reserved_keyword, platform in product(WIN_RESERVED_FILE_NAMES, ["windows"])
        ]
        + [
            ["{}\\{}".format(drive, filename), platform, "{}\\{}_".format(drive, filename)]
            for drive, platform, filename in product(
                ["C:", "D:"], ["windows"], NTFS_RESERVED_FILE_NAMES
            )
        ],
    )
    def test_normal_reserved_name(self, value, test_platform, expected):
        filename = sanitize_filepath(value, platform=test_platform)
        assert filename == expected
        assert is_valid_filepath(filename, platform=test_platform)

    @pytest.mark.parametrize(
        ["value", "check_reserved", "expected"],
        [
            ["CON", True, "CON_"],
            ["CON", False, "CON"],
        ],
    )
    def test_normal_check_reserved(self, value, check_reserved, expected):
        assert (
            sanitize_filepath(value, platform="windows", check_reserved=check_reserved) == expected
        )

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            [Path("AA" + c + "B"), rep, Path("AA" + rep + "B")]
            for c, rep in product(SANITIZE_CHARS, REPLACE_TEXTS)
        ]
        + [
            [Path("A" + c + "B"), rep, Path("A" + c + "B")]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXTS)
        ]
        + [
            [Path("あ" + c + "い"), rep, Path("あ" + c + "い")]
            for c, rep in product(NOT_SANITIZE_CHARS, REPLACE_TEXTS)
        ],
    )
    def test_normal_pathlike(self, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text)
        assert sanitized_name == expected
        assert is_pathlike_obj(sanitized_name)

        validate_filepath(sanitized_name)
        assert is_valid_filepath(sanitized_name)

    @pytest.mark.parametrize(
        ["test_platform", "value", "expected"],
        [
            ["linux", "a/b/c.txt", "a/b/c.txt"],
            ["linux", "a//b?/c.txt", "a/b?/c.txt"],
            ["linux", "../a/./../b/c.txt", "../b/c.txt"],
            ["windows", "a/b/c.txt", "a\\b\\c.txt"],
            ["windows", "a//b?/c.txt", "a\\b\\c.txt"],
            ["windows", "../a/./../b/c.txt", "..\\b\\c.txt"],
            ["universal", "a/b/c.txt", "a/b/c.txt"],
            ["universal", "./", "."],
            ["universal", "./a/b/c.txt", "a/b/c.txt"],
            ["universal", "../a/./../b/c.txt", "../b/c.txt"],
            ["universal", "a//b?/c.txt", "a/b/c.txt"],
        ],
    )
    def test_normal_relative_path(self, test_platform, value, expected):
        assert sanitize_filepath(value, platform=test_platform) == expected

    @pytest.mark.parametrize(
        ["test_platform", "value", "expected"],
        [
            ["linux", "a/b/c.txt", "a/b/c.txt"],
            ["linux", "a//b?/c.txt", "a/b?/c.txt"],
            ["linux", "../a/./../b/c.txt", "../a/./../b/c.txt"],
            ["windows", "a/b/c.txt", "a\\b\\c.txt"],
            ["windows", "a//b?/c.txt", "a\\b\\c.txt"],
            ["windows", "../a/./../b/c.txt", "..\\a\\.\\..\\b\\c.txt"],
            ["universal", "a/b/c.txt", "a/b/c.txt"],
            ["universal", "./", "."],
            ["universal", "./a/b/c.txt", "./a/b/c.txt"],
            ["universal", "../a/./../b/c.txt", "../a/./../b/c.txt"],
            ["universal", "a//b?/c.txt", "a/b/c.txt"],
        ],
    )
    def test_normal_not_normalize(self, test_platform, value, expected):
        assert sanitize_filepath(value, platform=test_platform, normalize=False) == expected

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["", ""],
            [None, ""],
        ],
    )
    def test_normal_null_values(self, value, expected):
        assert sanitize_filepath(value) == expected

    @pytest.mark.parametrize(
        ["test_platform", "value", "replace_text", "expected"],
        [
            ["linux", "/tmp/あいう\0えお.txt", "", "/tmp/あいうえお.txt"],
            ["linux", "/tmp/属\0性.txt", "-", "/tmp/属-性.txt"],
            ["universal", "tmp/あいう\0えお.txt", "", "tmp/あいうえお.txt"],
            ["universal", "tmp/属\0性.txt", "-", "tmp/属-性.txt"],
        ],
    )
    def test_normal_multibyte(self, test_platform, value, replace_text, expected):
        sanitized_name = sanitize_filepath(value, replace_text, platform=test_platform)
        assert sanitized_name == expected
        validate_filepath(sanitized_name, platform=test_platform)
        assert is_valid_filepath(sanitized_name, platform=test_platform)

    @pytest.mark.parametrize(
        ["platform", "value", "expected"],
        [
            ["windows", "a/b", "a\\b"],
            ["windows", "a\\b", "a\\b"],
            ["windows", "a\\\\b", "a\\b"],
            ["linux", "a/b", "a/b"],
            ["linux", "a//b", "a/b"],
            ["linux", "a\\b", "a/b"],
            ["linux", "a\\\\b", "a/b"],
            ["universal", "a/b", "a/b"],
            ["universal", "a//b", "a/b"],
            ["universal", "a\\b", "a/b"],
            ["universal", "a\\\\b", "a/b"],
        ],
    )
    def test_normal_path_separator(self, platform, value, expected):
        sanitized = sanitize_filepath(value, platform=platform)
        assert sanitized == expected
        assert is_valid_filepath(sanitized, platform=platform)

    @pytest.mark.skipif(m_platform.system() != "Windows", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["C:\\a\\b|c.txt", "C:\\a\\bc.txt"],
        ],
    )
    def test_auto_platform_win(self, value, expected):
        if isinstance(expected, str):
            sanitized = sanitize_filepath(value, platform="auto")
            assert is_valid_filepath(sanitized, platform="auto")
        else:
            with pytest.raises(expected):
                sanitize_filepath(value, platform="auto")

    @pytest.mark.skipif(m_platform.system() != "Linux", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["C:\\a\\b\\c.txt", ValidationError],
        ],
    )
    def test_auto_platform_linux(self, value, expected):
        if isinstance(expected, str):
            sanitized = sanitize_filepath(value, platform="auto")
            assert is_valid_filepath(sanitized, platform="auto")
        else:
            with pytest.raises(expected):
                sanitize_filepath(value, platform="auto")

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    @pytest.mark.parametrize(
        ["value", "expected"],
        [[1, TypeError], [True, TypeError], [nan, TypeError], [inf, TypeError]],
    )
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            sanitize_filepath(value)
        assert not is_valid_filepath(value)
