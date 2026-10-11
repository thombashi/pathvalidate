import pytest

from pathvalidate import sanitize_filename, sanitize_filepath


@pytest.mark.parametrize("replacement", [r"\n", r"\1", r"\g<0>", "\\"])
def test_filename_replacement_is_literal(replacement):
    assert sanitize_filename("a/b", replacement_text=replacement, platform="linux") == (
        "a" + replacement + "b"
    )


@pytest.mark.parametrize("replacement", [r"\n", r"\1", r"\g<0>"])
def test_filepath_replacement_is_literal(replacement):
    assert sanitize_filepath(
        "a\x00b", replacement_text=replacement, platform="linux", normalize=False
    ) == ("a" + replacement.replace("\\", "/") + "b")


@pytest.mark.parametrize("replacement", [r"\n", r"\1", r"\g<0>", "\\"])
def test_reserved_name_handler_replacement_is_literal(replacement):
    assert (
        sanitize_filename(
            "reserved",
            platform="linux",
            additional_reserved_names=["reserved"],
            reserved_name_handler=lambda error: replacement,
        )
        == replacement
    )
