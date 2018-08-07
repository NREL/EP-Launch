#!/bin/bash

pip install --upgrade --pre https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-14.04/wxPython-4.0.3-cp36-cp36m-linux_x86_64.whl
python setup.py build && tar -zcvf eplaunch.tar.gz build/exe.linux-x86_64-3.6
