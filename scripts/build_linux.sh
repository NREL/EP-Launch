#!/usr/bin/env bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
SHA=`echo ${TRAVIS_COMMIT} | cut -c 1-6`
pyinstaller eplaunch.spec
tar -zcf EP-Launch-linux-${VERSION}-${SHA}.tar.gz dist/EPLaunch
mkdir tmp_build
cp EP-Launch-linux-${VERSION}-${SHA}.tar.gz tmp_build
