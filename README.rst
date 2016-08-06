pathvalidate
============

.. image:: https://img.shields.io/pypi/pyversions/pathvalidate.svg
    :target: https://pypi.python.org/pypi/pathvalidate
.. image:: https://travis-ci.org/thombashi/pathvalidate.svg?branch=master
    :target: https://travis-ci.org/thombashi/pathvalidate
.. image:: https://ci.appveyor.com/api/projects/status/oygpr3q8bqitrl3y/branch/master?svg=true
    :target: https://ci.appveyor.com/project/thombashi/pathvalidate/branch/master
.. image:: https://coveralls.io/repos/github/thombashi/pathvalidate/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/pathvalidate?branch=master

Summary
-------

pathvalidate is a python library to validate/sanitize a string such as filename/variable-name/excel-sheet-name.

Examples
========

Validate a filename
-------------------

.. code:: python

    import pathvalidate

    try:
        pathvalidate.validate_filename("_a*b:c<d>e%f/(g)h+i_0.txt")
    except ValueError:
        print("invalid filename!")

.. code::

    invalid filename!

Sanitize a filename
-------------------

.. code:: python

    import pathvalidate

    filename = "_a*b:c<d>e%f/(g)h+i_0.txt"
    print(pathvalidate.sanitize_filename(filename))

.. code::

    _abcde%f(g)h+i_0.txt

Sanitize a variable name
------------------------

.. code:: python

    import pathvalidate

    print(pathvalidate.sanitize_python_var_name("_a*b:c<d>e%f/(g)h+i_0.txt"))

.. code::

    abcdefghi_0txt

For more information
--------------------

More examples are available at 
http://pathvalidate.readthedocs.org/en/latest/pages/examples/index.html

Installation
============

::

    pip install pathvalidate


Dependencies
============

Python 2.7 or 3.3+

- `DataPropery <https://github.com/thombashi/DataProperty>`__


Test dependencies
-----------------

- `pytest <http://pytest.org/latest/>`__
- `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
- `tox <https://testrun.org/tox/latest/>`__

Documentation
=============

http://pathvalidate.readthedocs.org/en/latest/

