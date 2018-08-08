#!/bin/bash

echo "|#*#| - Inside install_wxpython, TRAVIS = ${TRAVIS}; TOX_ENV = ${TOX_ENV}"
echo "Bash version: ${BASH_VERSION}"

if [[ -v TRAVIS ]]; then
    if [[ "a${TOX_ENV}" == "apackage" ]]; then
        pip install https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-14.04/wxPython-4.0.3-cp36-cp36m-linux_x86_64.whl
    elif [[ "a${TOX_ENV}" == "amac" ]]; then
        pip install wxpython
    fi
fi
