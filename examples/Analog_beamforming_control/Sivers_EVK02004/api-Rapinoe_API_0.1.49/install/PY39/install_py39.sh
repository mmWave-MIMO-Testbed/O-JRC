#!/bin/bash

# PYTHON 3.9 INSTALLATION
if py39="$(python3.9 -V 2>&1)"; then
    echo "Python 3.9 found!"
    PYCMD=python3.9

    $PYCMD -m pip install --upgrade pip

    echo Installing requirements ...
    $PYCMD -m pip install -r ../requirements.txt

    echo ""
    echo ""
    echo "Installation for Python 3.9 complete!"
else
    echo "Python 3.9 not found!"
fi

sleep 3

