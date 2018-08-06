#!/bin/bash

python setup.py build && tar -zcvf eplaunch.tar.gz build/exe.linux-x86_64-3.6
