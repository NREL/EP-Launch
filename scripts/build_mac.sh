#!/bin/bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
pip install wxpython
pyinstaller --onefile --windowed eplaunch.spec
ls dist/*
tar -zcf EP-Launch-${VERSION}-mac.tar.gz dist/eplaunch.app
mkdir tmp_build
cp EP-Launch-${VERSION}-mac.tar.gz tmp_build
