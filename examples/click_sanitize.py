#!/usr/bin/env python3

import click

from pathvalidate.click import sanitize_filename_arg, sanitize_filepath_arg


@click.command()
@click.option("--filename", callback=sanitize_filename_arg)
@click.option("--filepath", callback=sanitize_filepath_arg)
def cli(filename, filepath):
    if filename:
        click.echo(f"filename: {filename}")
    if filepath:
        click.echo(f"filepath: {filepath}")


if __name__ == "__main__":
    cli()
