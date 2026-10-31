"""Length policies at the public filename and filepath boundaries."""

import codecs
from pathlib import Path, PurePosixPath, PureWindowsPath
from unittest.mock import Mock

import pytest

import pathvalidate as pv
from pathvalidate.handler import ReservedNameHandler, raise_error


@pytest.fixture(params=["function", "class"])
def filename(request):
    def sanitize(value, replacement_text="", **kwargs):
        kwargs.setdefault("platform", "linux")
        kwargs.setdefault("fs_encoding", "utf-8")
        if request.param == "function":
            return pv.sanitize_filename(value, replacement_text=replacement_text, **kwargs)
        return pv.FileNameSanitizer(**kwargs).sanitize(value, replacement_text)

    return sanitize


@pytest.fixture(params=["function", "class"])
def filepath(request):
    def sanitize(value, **kwargs):
        kwargs.setdefault("platform", "linux")
        kwargs.setdefault("fs_encoding", "utf-8")
        if request.param == "function":
            return pv.sanitize_filepath(value, **kwargs)
        return pv.FilePathSanitizer(**kwargs).sanitize(value)

    return sanitize


@pytest.fixture(params=["string", "enum"])
def behavior(request):
    return lambda value: value if request.param == "string" else pv.LengthBehavior(value)


def assert_length_error(error, value, budget, encoding="utf-8", platform=pv.Platform.LINUX):
    assert error.reason == pv.ErrorReason.INVALID_LENGTH
    assert error.platform == platform
    assert error.fs_encoding == encoding
    assert error.byte_count == len(value.encode(encoding))
    assert error.as_slog()["value"] == value
    assert f"expected<={budget} bytes" in str(error)
    assert f"actual={len(value.encode(encoding))} bytes" in str(error)


def test_public_enum():
    assert {member.name: member.value for member in pv.LengthBehavior} == {
        "KEEP": "keep",
        "TRIM": "trim",
        "TRIM_NAME": "trim_name",
        "ERROR": "error",
    }
    assert "LengthBehavior" in pv.__all__


@pytest.mark.parametrize(
    "mode, expected", [("keep", "abcdefgh.txt"), ("trim", "abcdefgh"), ("trim_name", "abcd.txt")]
)
def test_filename_policies(filename, behavior, mode, expected):
    assert filename("abcdefgh.txt", max_len=8, length_behavior=behavior(mode)) == expected


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
def test_exact_boundary(filename, behavior, mode):
    assert filename("abcd.txt", max_len=8, length_behavior=behavior(mode)) == "abcd.txt"


@pytest.mark.parametrize("post", [False, True])
def test_error_metadata(filename, behavior, post):
    with pytest.raises(pv.ValidationError) as exc:
        filename(
            "abcdefgh.txt",
            max_len=8,
            length_behavior=behavior("error"),
            validate_after_sanitize=post,
        )
    assert_length_error(exc.value, "abcdefgh.txt", 8)


def test_keep_final_validation(filename, behavior):
    with pytest.raises(pv.ValidationError) as exc:
        filename(
            "abcdefgh.txt",
            max_len=8,
            length_behavior=behavior("keep"),
            validate_after_sanitize=True,
        )
    assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE
    assert "PV1101" in exc.value.description


@pytest.mark.parametrize(
    "value,budget,expected",
    [
        ("archive.tar.gz", 10, "archive.gz"),
        (".bashrc", 4, ".bas"),
        (".config.json", 8, ".co.json"),
        ("...txt", 4, "...t"),
        ("abc.txt", 4, ".txt"),
        ("filename.", 6, "filen."),
        ("abcdef", 3, "abc"),
        (".", 1, "."),
        ("..", 1, "."),
    ],
)
def test_extension_rules(filename, behavior, value, budget, expected):
    assert filename(value, max_len=budget, length_behavior=behavior("trim_name")) == expected


@pytest.mark.parametrize(
    "value,budget,encoding,expected",
    [
        ("あいう.txt", 10, "utf-8", "あい.txt"),
        ("あいう.txt", 12, "utf-16", "あ.txt"),
        ("😀ab.txt", 12, "utf-16-le", "😀.txt"),
        ("😀ab.txt", 12, "utf-16-be", "😀.txt"),
        ("😀ab.txt", 11, "utf-16-le", ".txt"),
        ("😀ab.txt", 11, "utf-16-be", ".txt"),
        ("e\u0301.txt", 6, "utf-8", "e.txt"),
        ("日本語.txt", 12, "iso2022_jp", "日.txt"),
        ("あいう.txt", 10, "UTF8", "あい.txt"),
        ("あいう.txt", 13, "utf-8-sig", "あい.txt"),
        ("😀ab.txt", 24, "utf-32", "😀.txt"),
    ],
)
def test_encoded_candidates(filename, behavior, value, budget, encoding, expected):
    result = filename(
        value, max_len=budget, fs_encoding=encoding, length_behavior=behavior("trim_name")
    )
    assert result == expected
    assert len(result.encode(encoding)) <= budget


@pytest.mark.parametrize(
    "value,budget,encoding",
    [
        ("abc.txt", 3, "utf-8"),
        ("abc.longextension", 4, "utf-8"),
        ("abc.txt", 1, "utf-16"),
    ],
)
def test_extension_cannot_fit(filename, behavior, value, budget, encoding):
    with pytest.raises(pv.ValidationError) as exc:
        filename(value, max_len=budget, fs_encoding=encoding, length_behavior=behavior("trim_name"))
    assert_length_error(exc.value, value, budget, encoding)
    assert "extension" in exc.value.description


def test_unicode_error_metadata(filename, behavior):
    with pytest.raises(pv.ValidationError) as exc:
        filename("あいう.txt", max_len=10, length_behavior=behavior("error"))
    assert_length_error(exc.value, "あいう.txt", 10)


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
@pytest.mark.parametrize(
    "encoding,error", [("ascii", UnicodeEncodeError), ("unknown-encoding", LookupError)]
)
def test_encoding_errors_propagate(filename, mode, encoding, error):
    with pytest.raises(error):
        filename("あ.txt", length_behavior=mode, fs_encoding=encoding)


def test_replacement_precedes_policy(filename, behavior):
    assert filename("ab/cdef", max_len=6, length_behavior=behavior("error")) == "abcdef"
    with pytest.raises(pv.ValidationError) as exc:
        filename("ab/cd", replacement_text="LONG", max_len=6, length_behavior=behavior("error"))
    assert_length_error(exc.value, "abLONGcd", 6)


@pytest.mark.parametrize(
    "value,budget,expected",
    [
        ("CON.txt", 3, "CON_.txt"),
        (" badname. ", 3, "badname"),
        ("custom.txt", 3, "custom_.txt"),
    ],
)
def test_keep_name_hygiene(filename, behavior, value, budget, expected):
    handler = Mock(side_effect=ReservedNameHandler.add_trailing_underscore)
    assert (
        filename(
            value,
            max_len=budget,
            platform="windows",
            additional_reserved_names=["custom"],
            reserved_name_handler=handler,
            length_behavior=behavior("keep"),
        )
        == expected
    )
    assert handler.call_count == (0 if value.startswith(" ") else 1)
    with pytest.raises(pv.ValidationError) as exc:
        filename(
            value,
            max_len=budget,
            platform="windows",
            additional_reserved_names=["custom"],
            length_behavior=behavior("keep"),
            validate_after_sanitize=True,
        )
    assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
def test_existing_reserved_substitution(filename, behavior, mode):
    assert (
        filename("CON.CON", max_len=20, platform="windows", length_behavior=behavior(mode))
        == "CON_.CON_"
    )


@pytest.mark.parametrize("post", [False, True])
def test_handler_growth_is_not_reprocessed(filename, behavior, post):
    handler = Mock(return_value="long-handler-output")
    kwargs = {
        "max_len": 3,
        "platform": "windows",
        "length_behavior": behavior("error"),
        "reserved_name_handler": handler,
        "validate_after_sanitize": post,
    }
    if post:
        with pytest.raises(pv.ValidationError) as exc:
            filename("CON", **kwargs)
        assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE
    else:
        assert filename("CON", **kwargs) == "long-handler-output"
    handler.assert_called_once()


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
@pytest.mark.parametrize("value", ["", "/"])
def test_null_handler(filename, behavior, mode, value):
    handler = Mock(side_effect=raise_error)
    with pytest.raises(pv.ValidationError) as exc:
        filename(value, length_behavior=behavior(mode), null_value_handler=handler)
    assert exc.value.reason == pv.ErrorReason.NULL_NAME
    handler.assert_called_once()


def test_no_extension_null_and_windows_trailing_dot(filename):
    assert filename("あ", max_len=1, length_behavior="trim_name") == ""
    with pytest.raises(pv.ValidationError) as exc:
        filename("あ", max_len=1, length_behavior="trim_name", validate_after_sanitize=True)
    assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE
    assert (
        filename("filename.", max_len=6, length_behavior="trim_name", platform="windows") == "filen"
    )
    with pytest.raises(pv.ValidationError) as exc:
        filename(" badname. ", max_len=3, platform="windows", length_behavior="error")
    assert_length_error(exc.value, " badname. ", 3, platform=pv.Platform.WINDOWS)


def test_path_component_and_total_budgets(filepath, behavior):
    kwargs = {"max_len": 8, "normalize": False, "length_behavior": behavior("trim_name")}
    assert filepath("abcdefgh.txt/ijklmnop.log", **kwargs) == "abcd.txt/ijkl.log"
    with pytest.raises(pv.ValidationError) as exc:
        filepath("abcdefgh.txt/ijklmnop.log", validate_after_sanitize=True, **kwargs)
    assert exc.value.reason == pv.ErrorReason.INVALID_LENGTH
    assert filepath("abc/def", max_len=3, length_behavior=behavior("error")) == "abc/def"
    with pytest.raises(pv.ValidationError) as exc:
        filepath(
            "abc/def", max_len=3, length_behavior=behavior("error"), validate_after_sanitize=True
        )
    assert exc.value.reason == pv.ErrorReason.INVALID_LENGTH
    with pytest.raises(pv.ValidationError) as exc:
        filepath("/abcdefgh.txt/end", max_len=8, length_behavior=behavior("error"))
    assert_length_error(exc.value, "abcdefgh.txt", 8)


@pytest.mark.parametrize(
    "mode,expected", [("keep", "abcdefgh.txt"), ("trim", "abcdefgh"), ("trim_name", "abcd.txt")]
)
def test_path_policies(filepath, behavior, mode, expected):
    assert filepath("abcdefgh.txt", max_len=8, length_behavior=behavior(mode)) == expected


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
def test_path_special_bypass(filepath, behavior, mode):
    kwargs = {"max_len": 2, "length_behavior": behavior(mode)}
    assert filepath("$Mft", **kwargs) == "$Mft_"
    with pytest.raises(pv.ValidationError) as exc:
        filepath("$Mft", validate_after_sanitize=True, **kwargs)
    assert exc.value.reason == pv.ErrorReason.INVALID_LENGTH


@pytest.mark.parametrize("normalize,expected", [(False, "/abc/./def/../ghi"), (True, "/abc/ghi")])
def test_path_dot_entries(filepath, normalize, expected):
    assert (
        filepath("/abc//./def/../ghi/", max_len=3, length_behavior="error", normalize=normalize)
        == expected
    )


@pytest.mark.parametrize(
    "value,expected",
    [
        ("C:\\abcdefgh.txt\\ijklmnop.log", "C:\\abcd.txt\\ijkl.log"),
        ("\\\\server\\share\\abcdefgh.txt", "\\\\server\\share\\abcd.txt"),
    ],
)
def test_drive_and_unc(filepath, value, expected):
    assert (
        filepath(value, max_len=8, platform="windows", normalize=False, length_behavior="trim_name")
        == expected
    )


@pytest.mark.parametrize("path_type", [Path, PurePosixPath, PureWindowsPath])
def test_path_return_types(filename, filepath, path_type):
    for sanitize in (filename, filepath):
        result = sanitize(path_type("abcdefgh.txt"), max_len=8, length_behavior="trim_name")
        assert type(result) is type(Path())
        assert result == Path("abcd.txt")
    assert filename(PurePosixPath("abc/def.txt"), max_len=8, length_behavior="trim_name") == Path(
        "abcd.txt"
    )


def test_input_types(filename, filepath):
    for sanitize in (filename, filepath):
        assert sanitize(Path(""), length_behavior="error") == Path(".")
        assert sanitize("", length_behavior="error") == ""
        with pytest.raises(TypeError):
            sanitize(123, length_behavior="keep")


@pytest.mark.parametrize("invalid", ["TRIM", "unknown", "", None, 1, [], {}])
def test_invalid_policy_is_early(filename, filepath, invalid):
    for sanitize in (filename, filepath):
        handler = Mock(return_value="null")
        with pytest.raises(ValueError):
            sanitize("", length_behavior=invalid, null_value_handler=handler)
        handler.assert_not_called()


@pytest.mark.parametrize("post", [False, True])
def test_injected_validator_protocol(post):
    validator = Mock(spec=pv.AbstractValidator)
    validator.validate.side_effect = pv.ValidationError(reason=pv.ErrorReason.INVALID_LENGTH)
    handler = Mock(return_value="reserved")
    sanitizer = pv.FileNameSanitizer(
        3, "utf-8", "windows", None, handler, None, post, validator, "keep"
    )
    if post:
        with pytest.raises(pv.ValidationError) as exc:
            sanitizer.sanitize("CON.txt")
        assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE
    else:
        assert sanitizer.sanitize("CON.txt") == "CON.txt"
    assert validator.validate.call_count == (2 if post else 1)
    assert all(call.args == ("CON.txt",) for call in validator.validate.call_args_list)
    handler.assert_not_called()


@pytest.mark.parametrize("post", [False, True])
def test_injected_path_validator_protocol(post):
    error = pv.ValidationError(reason=pv.ErrorReason.INVALID_LENGTH)
    validator = Mock(spec=pv.AbstractValidator)
    validator.validate.side_effect = error
    handler = Mock(side_effect=ReservedNameHandler.add_trailing_underscore)
    sanitizer = pv.FilePathSanitizer(
        3, "utf-8", "windows", None, handler, None, False, post, validator, "keep"
    )
    if post:
        # The ordinary component's requested final validation runs first.
        with pytest.raises(pv.ValidationError) as exc:
            sanitizer.sanitize("CON.txt")
        assert exc.value.reason == pv.ErrorReason.INVALID_AFTER_SANITIZE
        validator.validate.assert_not_called()
    else:
        assert sanitizer.sanitize("CON.txt") == "CON_.txt"
        validator.validate.assert_called_once_with("CON_.txt")
    handler.assert_called_once()


@pytest.mark.parametrize("post", [False, True])
def test_custom_path_final_error_is_unchanged(post):
    error = pv.ValidationError(reason=pv.ErrorReason.INVALID_CHARACTER)
    validator = Mock(spec=pv.AbstractValidator)
    validator.validate.side_effect = error
    sanitizer = pv.FilePathSanitizer(
        3, "utf-8", "linux", None, None, None, False, post, validator, "keep"
    )
    if post:
        with pytest.raises(pv.ValidationError) as exc:
            sanitizer.sanitize("abc")
        assert exc.value is error
    else:
        assert sanitizer.sanitize("abc") == "abc"
    assert validator.validate.call_count == (2 if post else 1)


def test_injected_concrete_filename_validator_keeps_length_priority():
    validator = pv.FileNameValidator(max_len=3, platform="windows", fs_encoding="utf-8")
    handler = Mock(side_effect=ReservedNameHandler.add_trailing_underscore)
    sanitizer = pv.FileNameSanitizer(
        max_len=3,
        platform="windows",
        fs_encoding="utf-8",
        length_behavior="keep",
        validator=validator,
        reserved_name_handler=handler,
    )
    assert sanitizer.sanitize("CON.txt") == "CON.txt"
    handler.assert_not_called()


def test_old_positional_arguments():
    assert (
        pv.sanitize_filename("abcdefgh.txt", "", "linux", 8, "utf-8", None, None, None, None, False)
        == "abcdefgh"
    )
    assert (
        pv.sanitize_filepath(
            "abcdefgh.txt", "", "linux", 8, "utf-8", None, None, None, None, False, False
        )
        == "abcdefgh"
    )
    validator = Mock(spec=pv.AbstractValidator)
    assert (
        pv.FileNameSanitizer(8, "utf-8", "linux", None, None, None, False, validator).sanitize(
            "abcdefgh.txt"
        )
        == "abcdefgh"
    )
    validator.validate.assert_called_once_with("abcdefgh")
    validator.reset_mock()
    assert (
        pv.FilePathSanitizer(
            8, "utf-8", "linux", None, None, None, False, False, validator
        ).sanitize("abcdefgh.txt")
        == "abcdefgh"
    )
    validator.validate.assert_called_once_with("abcdefgh")


@pytest.mark.parametrize("mode", ["keep", "trim", "trim_name", "error"])
@pytest.mark.parametrize(
    "platform,limit", [("linux", 4096), ("windows", 260), ("macos", 1024), ("universal", 260)]
)
@pytest.mark.parametrize("budget", [0, -1, 10000])
def test_effective_budgets_unchanged(mode, platform, limit, budget):
    for sanitizer_type in (pv.FileNameSanitizer, pv.FilePathSanitizer):
        assert (
            sanitizer_type(max_len=budget, platform=platform, length_behavior=mode).max_len == limit
        )


def test_none_and_default_budgets(filename):
    assert len(filename("a" * 300)) == 255
    for sanitize in (pv.sanitize_filename, pv.sanitize_filepath):
        assert len(sanitize("a" * 5000, max_len=None, platform="linux")) == 4096
    # None is supported by the wrappers, not the existing class constructors.
    for sanitizer_type in (pv.FileNameSanitizer, pv.FilePathSanitizer):
        with pytest.raises(TypeError):
            sanitizer_type(max_len=None)


@pytest.mark.parametrize("sanitize", [pv.sanitize_filename, pv.sanitize_filepath])
def test_deprecated_check_reserved(sanitize):
    with pytest.warns(DeprecationWarning):
        assert (
            sanitize(
                "CON.txt",
                platform="windows",
                max_len=3,
                check_reserved=False,
                length_behavior="keep",
            )
            == "CON.txt"
        )


@pytest.mark.parametrize(
    "encoding,value,budget,expected",
    [
        ("iso2022_jp", "日本語", 8, "日本"),
        ("utf-7", "日本語", 7, "日本"),
        ("utf-16", "あ", 1, ""),
    ],
)
def test_shared_trim_behavior_remains(filename, encoding, value, budget, expected):
    for mode in ("trim", "trim_name"):
        assert (
            filename(value, max_len=budget, fs_encoding=encoding, length_behavior=mode) == expected
        )


def test_nonmonotonic_codec(filename):
    # A registered codec can shrink a longer prefix, even when the extension
    # alone exceeds the budget. Neither early rejection nor bisection is valid.
    lengths = {
        ".txt": 10,
        "a.txt": 5,
        "ab.txt": 7,
        "abc.txt": 12,
        "abcd.txt": 9,
        "abcde.txt": 6,
        "abcdef.txt": 15,
    }

    def encode(value, errors="strict"):
        return b"x" * lengths[value], len(value)

    def search(name):
        if name == "pathvalidate_nonmonotonic":
            return codecs.CodecInfo(name=name, encode=encode, decode=None)
        return None

    codecs.register(search)
    assert (
        filename(
            "abcdef.txt",
            max_len=6,
            fs_encoding="pathvalidate_nonmonotonic",
            length_behavior="trim_name",
        )
        == "abcde.txt"
    )
