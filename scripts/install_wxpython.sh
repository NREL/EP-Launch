#!/bin/bash

if [[ -v TRAVIS ]]; then
    pip install https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-14.04/wxPython-4.0.3-cp36-cp36m-linux_x86_64.whl
fi
