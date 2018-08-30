#!/usr/bin/env bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
SHA=`echo ${TRAVIS_COMMIT} | cut -c 1-8`
pyinstaller eplaunch.spec
tar -C dist -zcf EP-Launch-${VERSION}-${SHA}-linux.tar.gz EPLaunch
mkdir tmp_build
cp EP-Launch-${VERSION}-${SHA}-linux.tar.gz tmp_build
