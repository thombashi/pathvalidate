#!/bin/sh

set -eux

PKG=pathvalidate
VERSION=$(python -c "import ${PKG}; print(${PKG}.__version__)")
TAG=v${VERSION}
ARCHIVE=${TAG}.tar.gz
WORK_DIR=ppa

mkdir -p ${WORK_DIR}
cd ${WORK_DIR}
rm -f ${ARCHIVE}
wget https://github.com/thombashi/${PKG}/archive/${ARCHIVE}
tar -xvf ${ARCHIVE}
mv ${ARCHIVE} ${PKG}_${VERSION}.orig.tar.gz

cd ${PKG}-${VERSION}/debian
debuild -S -sa
