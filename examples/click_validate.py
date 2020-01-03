#!/usr/bin/env python3

import click

from pathvalidate.click import filename, filepath


@click.command()
@click.option("--filename", callback=filename)
@click.option("--filepath", callback=filepath)
def cli(filename, filepath):
    click.echo(filename, filepath)


if __name__ == "__main__":
    cli()
