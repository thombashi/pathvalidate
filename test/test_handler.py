import re

import pytest

from pathvalidate import ErrorReason, ValidationError
from pathvalidate.handler import raise_error, return_null_string, return_timestamp


timstamp_regexp = re.compile(r"^\d+\.\d+$")


class Test_return_null_string:
    @pytest.mark.parametrize(
        ["exception"],
        [
            [
                ValidationError(
                    description="hoge",
                    reason=ErrorReason.INVALID_CHARACTER,
                )
            ],
            [
                ValidationError(
                    description="foo",
                    reason=ErrorReason.INVALID_AFTER_SANITIZE,
                )
            ],
        ],
    )
    def test_normal(self, exception):
        assert return_null_string(exception) == ""


class Test_return_timestamp:
    @pytest.mark.parametrize(
        ["exception"],
        [
            [
                ValidationError(
                    description="hoge",
                    reason=ErrorReason.INVALID_CHARACTER,
                )
            ],
            [
                ValidationError(
                    description="foo",
                    reason=ErrorReason.INVALID_AFTER_SANITIZE,
                )
            ],
        ],
    )
    def test_normal(self, exception):
        assert timstamp_regexp.search(return_timestamp(exception)) is not None


class Test_raise_error:
    @pytest.mark.parametrize(
        ["exception"],
        [
            [
                ValidationError(
                    description="hoge",
                    reason=ErrorReason.INVALID_CHARACTER,
                )
            ],
            [
                ValidationError(
                    description="foo",
                    reason=ErrorReason.INVALID_AFTER_SANITIZE,
                )
            ],
        ],
    )
    def test_normal(self, exception):
        with pytest.raises(ValidationError) as e:
            raise_error(exception)
        assert exception == e.value
