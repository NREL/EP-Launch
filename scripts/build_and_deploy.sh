#!/bin/bash

pip install --upgrade --pre https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/wxPython-4.0.0b2-cp36-cp36mu-linux_x86_64.whl
python setup.py build && tar -zcvf eplaunch.tar.gz build/exe.linux-x86_64-3.6
