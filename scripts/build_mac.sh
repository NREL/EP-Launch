#!/bin/bash

pip install wxpython
python setup.py bdist_mac
tar -zcf eplaunch-mac.tar.gz build/EP-Launch-0.1.app
exit 0
