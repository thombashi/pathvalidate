#!/bin/sh

set -eux

PKG=pathvalidate
VERSION=0.27.1
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
