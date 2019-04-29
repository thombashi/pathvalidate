#!/bin/sh

set -eux

PKG=pathvalidate
VERSION=$(python -c "import pathvalidate as pv; print(pv.__version__)")
TAG=v${VERSION}
ARCHIVE=${TAG}.tar.gz
WORK_DIR=ppa

mkdir -p ${WORK_DIR}
cd ${WORK_DIR}
rm -f ${ARCHIVE}
wget https://github.com/thombashi/pathvalidate/archive/${ARCHIVE}
tar -xvf ${ARCHIVE}
mv ${ARCHIVE} ${PKG}_${VERSION}.orig.tar.gz

cd ${PKG}-${VERSION}/debian
debuild -S -sa
