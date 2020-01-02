#!/bin/sh

if [ "$TOXENV" != "cov" ] ; then
    tox
else
    pip install pytest-cov coveralls[toml] --upgrade
    python setup.py test --addopts "-v --cov"
    coveralls
fi
