#!/bin/bash

echo "|#*#| Inside build_and_deploy.sh"

pip install --upgrade --pre https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-14.04/wxPython-4.0.3-cp36-cp36m-linux_x86_64.whl
echo "Made it past wxPython installation"

python setup.py build
echo "Made it past setup.py build command"

tar -zcf eplaunch.tar.gz build/exe.linux-x86_64-3.6
echo "Made it past archiving stage"

echo "|#*#| Testing if archive exists:"
test -f /etc/bebebe
echo $?