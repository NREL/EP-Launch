#!/usr/bin/env bash

python setup.py build
tar -zcf EP-Launch-${VERSION}-linux.tar.gz build/exe.linux-x86_64-3.6
mkdir tmp_build
cp EP-Launch-${VERSION}-linux.tar.gz tmp_build
