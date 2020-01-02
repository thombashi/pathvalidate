#!/bin/sh

if [ "$TOXENV" != "cov" ] ; then
    tox
else
    tox
    coveralls
fi
