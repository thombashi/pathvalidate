pathvalidate
==============
.. image:: https://badge.fury.io/py/pathvalidate.svg
    :target: https://badge.fury.io/py/pathvalidate

.. image:: https://img.shields.io/pypi/pyversions/pathvalidate.svg
    :target: https://pypi.python.org/pypi/pathvalidate

.. image:: https://img.shields.io/travis/thombashi/pathvalidate/master.svg?label=Linux/macOS
    :target: https://travis-ci.org/thombashi/pathvalidate
    :alt: Linux CI test status

.. image:: https://img.shields.io/appveyor/ci/thombashi/pathvalidate/master.svg?label=Windows
    :target: https://ci.appveyor.com/project/thombashi/pathvalidate/branch/master
    :alt: Windows CI test status

.. image:: https://coveralls.io/repos/github/thombashi/pathvalidate/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/pathvalidate?branch=master

.. image:: https://img.shields.io/github/stars/thombashi/pathvalidate.svg?style=social&label=Star
   :target: https://github.com/thombashi/pathvalidate

Summary
---------
A Python library to validate/sanitize a string such as filenames/file-paths/variable-names/excel-sheet-names.

Features
---------

- Validate/Sanitize a string:
    - file name
    - file path
    - variable name: ``Python``/``JavaScript``
    - `Labeled Tab-separated Values (LTSV) <http://ltsv.org/>`__ label
    - Elastic search index name
    - Excel sheet name
    - SQLite table/attribute name

Examples
==========
Validate a filename
---------------------
:Sample Code:
    .. code-block:: python

        import pathvalidate

        try:
            pathvalidate.validate_filename("\0_a*b:c<d>e%f/(g)h+i_0.txt")
        except ValueError:
            print("invalid filename!")

:Output:
    .. code-block::

        invalid filename!

Sanitize a filename
---------------------
:Sample Code:
    .. code-block:: python

        import pathvalidate

        filename = "_a*b:c<d>e%f/(g)h+i_0.txt"
        print(pathvalidate.sanitize_filename(filename))

:Output:
    .. code-block::

        _abcde%f(g)h+i_0.txt

Sanitize a variable name
--------------------------
:Sample Code:
    .. code-block:: python

        import pathvalidate

        print(pathvalidate.sanitize_python_var_name("_a*b:c<d>e%f/(g)h+i_0.txt"))

:Output:
    .. code-block::

        abcdefghi_0txt

For more information
----------------------
More examples are available at 
http://pathvalidate.rtfd.io/en/latest/pages/examples/index.html

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
- `pytest <http://pytest.org/latest/>`__
- `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
- `tox <https://testrun.org/tox/latest/>`__

Documentation
===============
http://pathvalidate.rtfd.io/

