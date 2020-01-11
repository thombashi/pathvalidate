import click
import pytest
from click.testing import CliRunner

from pathvalidate.click import (
    sanitize_filename_arg,
    sanitize_filepath_arg,
    validate_filename_arg,
    validate_filepath_arg,
)


@click.command()
@click.option("--filename", callback=validate_filename_arg)
@click.option("--filepath", callback=validate_filepath_arg)
def cli_validate(filename, filepath):
    if filename:
        click.echo(filename)
    if filepath:
        click.echo(filepath)


@click.command()
@click.option("--filename", callback=sanitize_filename_arg)
@click.option("--filepath", callback=sanitize_filepath_arg)
def cli_sanitize(filename, filepath):
    if filename:
        click.echo(filename)
    if filepath:
        click.echo(filepath)


class Test_validate:
    @pytest.mark.parametrize(["value", "expected"], [["ab", 0], ["", 0], ["a/b", 2], ["a/?b", 2]])
    def test_normal_filename(self, value, expected):
        runner = CliRunner()
        result = runner.invoke(cli_validate, ["--filename", value])
        assert result.exit_code == expected

    @pytest.mark.parametrize(["value", "expected"], [["ab", 0], ["", 0], ["a/b", 0], ["a/?b", 2]])
    def test_normal_filepath(self, value, expected):
        runner = CliRunner()
        result = runner.invoke(cli_validate, ["--filepath", value])
        assert result.exit_code == expected


class Test_sanitize:
    @pytest.mark.parametrize(
        ["value", "expected"], [["ab", "ab"], ["", ""], ["a/b", "ab"], ["a/?b", "ab"]]
    )
    def test_normal_filename(self, value, expected):
        runner = CliRunner()
        result = runner.invoke(cli_sanitize, ["--filename", value])
        assert result.output.strip() == expected

    @pytest.mark.parametrize(
        ["value", "expected"], [["ab", "ab"], ["", ""], ["a/b", "a/b"], ["a/?b", "a/b"]]
    )
    def test_normal_filepath(self, value, expected):
        runner = CliRunner()
        result = runner.invoke(cli_sanitize, ["--filepath", value])
        assert result.output.strip() == expected
