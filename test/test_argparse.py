from argparse import ArgumentError, ArgumentParser

import pytest

from pathvalidate.argparse import (
    sanitize_filename_arg,
    sanitize_filepath_arg,
    validate_filename_arg,
    validate_filepath_arg,
)


class Test_validate_filename_arg:
    @pytest.mark.parametrize(["value"], [["abc"], ["abc.txt"]])
    def test_normal(self, value):
        parser = ArgumentParser()
        parser.add_argument("filename", type=validate_filename_arg)

        assert parser.parse_args([value]).filename == value

    @pytest.mark.parametrize(["value"], [["foo/abc"], ["a?c"], ["COM1"], ["a" * 8000]])
    def test_exception(self, value):
        parser = ArgumentParser()
        parser.add_argument("filename", type=validate_filename_arg)

        try:
            parser.parse_args([value])
        except SystemExit as e:
            assert isinstance(e.__context__, ArgumentError)
        else:
            raise RuntimeError()


class Test_validate_filepath_arg:
    @pytest.mark.parametrize(["value"], [["foo/abc"], ["foo/abc.txt"]])
    def test_normal(self, value):
        parser = ArgumentParser()
        parser.add_argument("filepath", type=validate_filepath_arg)

        assert parser.parse_args([value]).filepath == value

    @pytest.mark.parametrize(["value"], [["foo/a?c"], ["COM1"], ["a" * 8000]])
    def test_exception(self, value):
        parser = ArgumentParser()
        parser.add_argument("filepath", type=validate_filepath_arg)

        try:
            parser.parse_args([value])
        except SystemExit as e:
            assert isinstance(e.__context__, ArgumentError)
        else:
            raise RuntimeError()


class Test_sanitize_filename_arg:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["abc", "abc"],
            ["abc.txt", "abc.txt"],
            ["foo/abc", "fooabc"],
            ["a?c", "ac"],
            ["COM1", "COM1_"],
        ],
    )
    def test_normal(self, value, expected):
        parser = ArgumentParser()
        parser.add_argument("filename", type=sanitize_filename_arg)
        assert parser.parse_args([value]).filename == expected


class Test_sanitize_filepath_arg:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["abc", "abc"],
            ["abc.txt", "abc.txt"],
            ["foo/abc", "foo/abc"],
            ["a?c", "ac"],
            ["COM1", "COM1_"],
        ],
    )
    def test_normal(self, value, expected):
        parser = ArgumentParser()
        parser.add_argument("filepath", type=sanitize_filepath_arg)
        assert parser.parse_args([value]).filepath == expected
