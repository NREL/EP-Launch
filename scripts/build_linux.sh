#!/usr/bin/env bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
pyinstaller eplaunch.spec
tar -zcf EP-Launch-${VERSION}-linux.tar.gz dist/EPLaunch
mkdir tmp_build
cp EP-Launch-${VERSION}-linux.tar.gz tmp_build
