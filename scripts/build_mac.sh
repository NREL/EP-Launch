#!/bin/bash

VERSION=`grep VERSION eplaunch/__init__.py | cut -d= -f2 | cut -d\" -f2`
SHA=`echo ${TRAVIS_COMMIT} | cut -c 1-8`
pip install wxpython
pyinstaller --onefile --windowed eplaunch.spec
ls dist/*
tar -C dist -zcf EPLaunch-${VERSION}-${SHA}-mac.tar.gz eplaunch.app
mkdir tmp_build
cp EPLaunch-${VERSION}-${SHA}-mac.tar.gz tmp_build
