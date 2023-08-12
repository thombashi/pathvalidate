import pytest

from pathvalidate import Platform
from pathvalidate.error import ErrorReason, ValidationError, _to_error_code


class Test_to_error_code:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [1, "PV0001"],
        ],
    )
    def test_normal(self, value, expected):
        assert _to_error_code(value) == expected


class Test_str:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [
                ValidationError(
                    description="hoge",
                    platform=Platform.UNIVERSAL,
                    reason=ErrorReason.INVALID_CHARACTER,
                ),
                "[PV1100] invalid characters found: platform=universal, description=hoge",
            ],
        ],
    )
    def test_normal(self, value, expected):
        assert str(value) == expected


class Test_as_slog:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [
                ValidationError(
                    description="hoge",
                    platform=Platform.UNIVERSAL,
                    reason=ErrorReason.INVALID_CHARACTER,
                ),
                {"code": "PV1100", "description": "hoge", "platform": "universal"},
            ],
        ],
    )
    def test_normal(self, value, expected):
        assert value.as_slog() == expected
