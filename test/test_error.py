import pytest

from pathvalidate.error import _to_error_code


class Test_to_error_code:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [1, "PV0001"],
        ],
    )
    def test_normal(self, value, expected):
        assert _to_error_code(value) == expected
