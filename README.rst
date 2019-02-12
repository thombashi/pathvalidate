.. contents:: **pathvalidate**
   :backlinks: top
   :depth: 2

Summary
=========
`pathvalidate <https://github.com/thombashi/pathvalidate>`__ is a Python library to sanitize/validate a string such as filenames/file-paths/etc.

.. image:: https://badge.fury.io/py/pathvalidate.svg
    :target: https://badge.fury.io/py/pathvalidate
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/pathvalidate.svg
    :target: https://pypi.org/project/pathvalidate
    :alt: Supported Python versions

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
            print(e, file=sys.stderr)

:Output:
    .. code-block::

        invalid char found: invalid-char=':, \*, /, ", \?, >, \|, <', value='fi:l*e/p"a?t>h|.t<xt', reason=ErrorReason.INVALID_CHARACTER

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

For more information
----------------------
More examples can be found at 
https://pathvalidate.rtfd.io/en/latest/pages/examples/index.html

Installation
============

::

    pip install pathvalidate


Dependencies
============
Python 2.7+ or 3.4+
No external dependencies.


Test dependencies
-----------------
- `pytest <https://docs.pytest.org/en/latest/>`__
- `pytest-runner <https://github.com/pytest-dev/pytest-runner>`__
- `tox <https://testrun.org/tox/latest/>`__

Documentation
===============
https://pathvalidate.rtfd.io/

