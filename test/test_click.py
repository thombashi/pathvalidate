import click
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
    def test_normal_filename(self):
        runner = CliRunner()
        result = runner.invoke(cli_validate, ["--filename", "a/b"])
        assert result.exit_code

    def test_normal_filepath(self):
        runner = CliRunner()
        result = runner.invoke(cli_validate, ["--filepath", "a/?b"])
        assert result.exit_code


class Test_sanitize:
    def test_normal_filename(self):
        runner = CliRunner()
        result = runner.invoke(cli_sanitize, ["--filename", "a/b"])
        assert result.output.strip() == "ab"

    def test_normal_filepath(self):
        runner = CliRunner()
        result = runner.invoke(cli_sanitize, ["--filepath", "a/?b"])
        assert result.output.strip() == "a/b"
