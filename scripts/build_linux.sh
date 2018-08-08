#!/usr/bin/env bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
python setup.py build
tar -zcf EP-Launch-${VERSION}-linux.tar.gz build/exe.linux-x86_64-3.6
mkdir tmp_build
cp EP-Launch-${VERSION}-linux.tar.gz tmp_build
