# encoding: utf-8

from __future__ import unicode_literals

from argparse import ArgumentError, ArgumentParser, ArgumentTypeError

import pytest

from pathvalidate.argparse import filename, filepath


class Test_argparse_filename_validator(object):
    @pytest.mark.parametrize(["value"], [["abc"], ["abc.txt"]])
    def test_normal(self, value):
        parser = ArgumentParser()
        parser.add_argument("filename", type=filename)

        assert parser.parse_args([value])
        assert filename(value)

    @pytest.mark.parametrize(["value"], [["foo/abc"], ["a?c"], ["COM1"], ["a" * 8000]])
    def test_exception(self, value):
        parser = ArgumentParser()
        parser.add_argument("filename", type=filename)

        try:
            parser.parse_args([value])
        except SystemExit as e:
            assert isinstance(e.__context__, ArgumentError)
        else:
            raise RuntimeError()

        with pytest.raises(ArgumentTypeError):
            filename(value)


class Test_argparse_filepath_validator(object):
    @pytest.mark.parametrize(["value"], [["foo/abc"], ["foo/abc.txt"]])
    def test_normal(self, value):
        parser = ArgumentParser()
        parser.add_argument("filepath", type=filepath)

        assert parser.parse_args([value])
        assert filepath(value)

    @pytest.mark.parametrize(["value"], [["foo/a?c"], ["COM1"], ["a" * 8000]])
    def test_exception(self, value):
        parser = ArgumentParser()
        parser.add_argument("filepath", type=filepath)

        try:
            parser.parse_args([value])
        except SystemExit as e:
            assert isinstance(e.__context__, ArgumentError)
        else:
            raise RuntimeError()

        with pytest.raises(ArgumentTypeError):
            filepath(value)
