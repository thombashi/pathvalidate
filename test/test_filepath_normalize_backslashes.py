from pathlib import Path

import pytest

from pathvalidate import sanitize_filepath


@pytest.mark.parametrize(
    "platform,separator", [("windows", "\\"), ("linux", "/"), ("universal", "/")]
)
@pytest.mark.parametrize("value", [r"a\b\..\c.txt", r"a/b\..\c.txt", r"a\.\c.txt"])
def test_normalize_backslash_separators(platform, separator, value):
    expected = separator.join(["a", "c.txt"])
    assert sanitize_filepath(value, platform=platform) == expected
    assert sanitize_filepath(Path(value), platform=platform) == Path(expected)


@pytest.mark.parametrize(
    "platform,separator", [("windows", "\\"), ("linux", "/"), ("universal", "/")]
)
def test_backslash_normalization_opt_out(platform, separator):
    value = r"a\b\..\c.txt"
    expected = separator.join(["a", "b", "..", "c.txt"])
    assert sanitize_filepath(value, platform=platform, normalize=False) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (r"C:\a\b\..\c.txt", r"C:\a\c.txt"),
        (r"C:a\b\..\c.txt", r"C:\a\c.txt"),
        (r"\\server\share\a\b\..\c.txt", r"\\server\share\a\c.txt"),
        (r"\a\b\..\c.txt", r"\a\c.txt"),
        (r"..\a\.\..\c.txt", r"..\c.txt"),
    ],
)
def test_normalize_backslash_windows_roots(value, expected):
    assert sanitize_filepath(value, platform="windows") == expected


@pytest.mark.parametrize("platform", ["windows", "linux", "universal"])
@pytest.mark.parametrize("value", [r"a\b\c.txt", "a/b/c.txt", "../a/b.txt"])
def test_backslash_separator_control(platform, value):
    separator = "\\" if platform == "windows" else "/"
    assert sanitize_filepath(value, platform=platform) == value.replace("\\", "/").replace(
        "/", separator
    )
