import pytest

from pathvalidate import is_valid_filename, sanitize_filename, sanitize_filepath
from pathvalidate.handler import ReservedNameHandler


@pytest.mark.parametrize("platform", ["windows", "universal"])
@pytest.mark.parametrize("filename", ["con.icon", "CON.CON.txt", "aux.aux", "COM1.COM1"])
@pytest.mark.parametrize(
    ["handler", "prefix", "suffix"],
    [
        [ReservedNameHandler.add_leading_underscore, "_", ""],
        [ReservedNameHandler.add_trailing_underscore, "", "_"],
    ],
)
def test_reserved_name_handler_preserves_extension(filename, platform, handler, prefix, suffix):
    stem, extension = filename.split(".", 1)
    expected = f"{prefix}{stem}{suffix}.{extension}"

    result = sanitize_filename(filename, platform=platform, reserved_name_handler=handler)

    assert result == expected
    assert is_valid_filename(result, platform=platform)


def test_additional_reserved_name_preserves_extension():
    assert (
        sanitize_filename("foo.foo", platform="linux", additional_reserved_names=["foo"])
        == "foo_.foo"
    )


def test_filepath_preserves_extension():
    assert sanitize_filepath("folder/con.icon", platform="windows") == r"folder\con_.icon"
