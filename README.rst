**pathvalidate**

.. image:: https://img.shields.io/pypi/pyversions/pathvalidate.svg
    :target: https://pypi.python.org/pypi/pathvalidate
.. image:: https://travis-ci.org/thombashi/pathvalidate.svg?branch=master
    :target: https://travis-ci.org/thombashi/pathvalidate
.. image:: https://coveralls.io/repos/github/thombashi/pathvalidate/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/pathvalidate?branch=master

.. contents:: Table of contents
   :backlinks: top
   :local:

Summary
=======
pathvalidate is a python library to validate filename.

Installation
============

::

    pip install pathvalidate

Usage
=====

Filename validation
-------------------

.. code:: python

    import pathvalidate

    filename = "a*b:c<d>e%f(g)h.txt"
    try:
        pathvalidate.validate_filename(filename)
    except ValueError:
        print("invalid filename!")

.. code:: console

    invalid filename!

Replace invalid chars
---------------------

.. code:: pythn

    import pathvalidate

    filename = "a*b:c<d>e%f(g)h.txt"
    print(pathvalidate.sanitize_filename(filename))

.. code:: console

    abcde%f(g)h+i.txt

Replace symbols
---------------

.. code:: pythn

    import pathvalidate

    filename = "a*b:c<d>e%f(g)h.txt"
    print(pathvalidate.replace_symbol(filename))

.. code:: console

    abcdefgh+itxt

Dependencies
============

Python 2.6+ or 3.3+

-  `DataPropery <https://github.com/thombashi/DataProperty>`__

Test dependencies
-----------------

-  `pytest <https://pypi.python.org/pypi/pytest>`__
-  `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
-  `tox <https://pypi.python.org/pypi/tox>`__
