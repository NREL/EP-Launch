#!/usr/bin/env bash

scripts/install_wxpython.sh
python setup.py build
tar -zcf EP-Launch-${VERSION}-linux.tar.gz build/exe.linux-x86_64-3.6