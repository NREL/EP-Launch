#!/bin/bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
pip install wxpython
python setup.py bdist_mac
tar -zcf EP-Launch-${VERSION}-mac.tar.gz build/EP-Launch-0.1.app
mkdir tmp_build
cp EP-Launch-${VERSION}-mac.tar.gz tmp_build
