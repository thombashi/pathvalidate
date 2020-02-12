.. contents:: **pathvalidate**
   :backlinks: top
   :depth: 2

Summary
=========
`pathvalidate <https://github.com/thombashi/pathvalidate>`__ is a Python library to sanitize/validate a string such as filenames/file-paths/etc.

.. image:: https://badge.fury.io/py/pathvalidate.svg
    :target: https://badge.fury.io/py/pathvalidate
    :alt: PyPI package version

.. image:: https://anaconda.org/thombashi/pathvalidate/badges/version.svg
    :target: https://anaconda.org/thombashi/pathvalidate
    :alt: conda package version

.. image:: https://img.shields.io/pypi/pyversions/pathvalidate.svg
    :target: https://pypi.org/project/pathvalidate
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/pathvalidate.svg
    :target: https://pypi.org/project/pathvalidate
    :alt: Supported Python implementations

.. image:: https://img.shields.io/travis/thombashi/pathvalidate/master.svg?label=Linux/macOS%20CI
    :target: https://travis-ci.org/thombashi/pathvalidate
    :alt: Linux/macOS CI status

.. image:: https://img.shields.io/appveyor/ci/thombashi/pathvalidate/master.svg?label=Windows%20CI
    :target: https://ci.appveyor.com/project/thombashi/pathvalidate/branch/master
    :alt: Windows CI status

.. image:: https://coveralls.io/repos/github/thombashi/pathvalidate/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/pathvalidate?branch=master
    :alt: Test coverage

.. image:: https://img.shields.io/github/stars/thombashi/pathvalidate.svg?style=social&label=Star
    :target: https://github.com/thombashi/pathvalidate
    :alt: GitHub stars

Features
---------
- Sanitize/Validate a string as a:
    - file name
    - file path
- filename/filepath validator/sanitizer for ``argparse``/``click``
- Multibyte character support

Examples
==========
Sanitize a filename
---------------------
:Sample Code:
    .. code-block:: python

        from pathvalidate import sanitize_filename

        fname = "fi:l*e/p\"a?t>h|.t<xt"
        print("{} -> {}".format(fname, sanitize_filename(fname)))

        fname = "\0_a*b:c<d>e%f/(g)h+i_0.txt"
        print("{} -> {}".format(fname, sanitize_filename(fname)))

:Output:
    .. code-block::

        fi:l*e/p"a?t>h|.t<xt -> filepath.txt
        _a*b:c<d>e%f/(g)h+i_0.txt -> _abcde%f(g)h+i_0.txt

Sanitize a filepath
---------------------
:Sample Code:
    .. code-block:: python

        from pathvalidate import sanitize_filepath

        fpath = "fi:l*e/p\"a?t>h|.t<xt"
        print("{} -> {}".format(fpath, sanitize_filepath(fpath)))

        fpath = "\0_a*b:c<d>e%f/(g)h+i_0.txt"
        print("{} -> {}".format(fpath, sanitize_filepath(fpath)))

:Output:
    .. code-block::

        fi:l*e/p"a?t>h|.t<xt -> file/path.txt
        _a*b:c<d>e%f/(g)h+i_0.txt -> _abcde%f/(g)h+i_0.txt

Validate a filename
---------------------
:Sample Code:
    .. code-block:: python

        import sys
        from pathvalidate import ValidationError, validate_filename

        try:
            validate_filename("fi:l*e/p\"a?t>h|.t<xt")
        except ValidationError as e:
            print("{}\n".format(e), file=sys.stderr)

        try:
            validate_filename("COM1")
        except ValidationError as e:
            print("{}\n".format(e), file=sys.stderr)

:Output:
    .. code-block::

        invalid char found: invalids=(':', '*', '/', '"', '?', '>', '|', '<'), value='fi:l*e/p"a?t>h|.t<xt', reason=INVALID_CHARACTER, target-platform=Windows

        'COM1' is a reserved name, reason=RESERVED_NAME, target-platform=universal

Check a filename
------------------
:Sample Code:
    .. code-block:: python

        from pathvalidate import is_valid_filename, sanitize_filename

        fname = "fi:l*e/p\"a?t>h|.t<xt"
        print("is_valid_filename('{}') return {}".format(fname, is_valid_filename(fname)))

        sanitized_fname = sanitize_filename(fname)
        print("is_valid_filename('{}') return {}".format(sanitized_fname, is_valid_filename(sanitized_fname)))

:Output:
    .. code-block::

        is_valid_filename('fi:l*e/p"a?t>h|.t<xt') return False
        is_valid_filename('filepath.txt') return True

filename/filepath validator for argparse
------------------------------------------
:Sample Code:
    .. code-block:: python

        from argparse import ArgumentParser

        from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg

        parser = ArgumentParser()
        parser.add_argument("--filepath", type=validate_filepath_arg)
        parser.add_argument("--filename", type=validate_filename_arg)
        options = parser.parse_args()

        if options.filename:
            print("filename: {}".format(options.filename))

        if options.filepath:
            print("filepath: {}".format(options.filepath))

:Output:
    .. code-block::

        $ ./examples/argparse_validate.py --filename eg
        filename: eg
        $ ./examples/argparse_validate.py --filepath e?g
        usage: argparse_validate.py [-h] [--filepath FILEPATH] [--filename FILENAME]
        argparse_validate.py: error: argument --filepath: invalid char found: invalids=('?'), value='e?g', reason=INVALID_CHARACTER, target-platform=Windows

.. note::
    ``validate_filepath_arg`` is set platform as ``"auto"``.

filename/filepath sanitizer for argparse
------------------------------------------
:Sample Code:
    .. code-block:: python

        from argparse import ArgumentParser

        from pathvalidate.argparse import sanitize_filename_arg, sanitize_filepath_arg


        parser = ArgumentParser()
        parser.add_argument("--filename", type=sanitize_filename_arg)
        parser.add_argument("--filepath", type=sanitize_filepath_arg)
        options = parser.parse_args()

        if options.filename:
            print("filename: {}".format(options.filename))

        if options.filepath:
            print("filepath: {}".format(options.filepath))

:Output:
    .. code-block::

        $ ./examples/argparse_sanitize.py --filename e/g
        filename: eg

.. note::
    ``sanitize_filepath_arg`` is set platform as ``"auto"``.

filename/filepath validator for click
---------------------------------------
:Sample Code:
    .. code-block:: python

        import click

        from pathvalidate.click import validate_filename_arg, validate_filepath_arg


        @click.command()
        @click.option("--filename", callback=validate_filename_arg)
        @click.option("--filepath", callback=validate_filepath_arg)
        def cli(filename, filepath):
            if filename:
                click.echo("filename: {}".format(filename))
            if filepath:
                click.echo("filepath: {}".format(filepath))


        if __name__ == "__main__":
            cli()

:Output:
    .. code-block::

        $ ./examples/click_validate.py --filename ab
        filename: ab
        $ ./examples/click_validate.py --filepath e?g
        Usage: click_validate.py [OPTIONS]

        Error: Invalid value for "--filepath": invalid char found: invalids=('?'), value='e?g', reason=INVALID_CHARACTER, target-platform=Windows

filename/filepath sanitizer for click
---------------------------------------
:Sample Code:
    .. code-block:: python

        import click

        from pathvalidate.click import sanitize_filename_arg, sanitize_filepath_arg


        @click.command()
        @click.option("--filename", callback=sanitize_filename_arg)
        @click.option("--filepath", callback=sanitize_filepath_arg)
        def cli(filename, filepath):
            if filename:
                click.echo("filename: {}".format(filename))
            if filepath:
                click.echo("filepath: {}".format(filepath))


        if __name__ == "__main__":
            cli()

:Output:
    .. code-block::

        $ ./examples/click_sanitize.py --filename a/b
        filename: ab

For more information
----------------------
More examples can be found at 
https://pathvalidate.rtfd.io/en/latest/pages/examples/index.html

Installation
============
Installation: pip
------------------------------
::

    pip install pathvalidate

Installation: conda
------------------------------
::

    conda install -c thombashi pathvalidate

Installation: apt
------------------------------
::

    sudo add-apt-repository ppa:thombashi/ppa
    sudo apt update
    sudo apt install python3-pathvalidate


Dependencies
============
Python 3.5+
No external dependencies.


Test dependencies
-----------------
- `pytest <https://docs.pytest.org/en/latest/>`__
- `tox <https://testrun.org/tox/latest/>`__

Documentation
===============
https://pathvalidate.rtfd.io/

