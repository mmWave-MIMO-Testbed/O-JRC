#!/bin/bash

# PYTHON 3.10 INSTALLATION
if py310="$(python3.10 -V 2>&1)"; then
    echo "Python 3.10 found!"
    PYCMD=python3.10

    $PYCMD -m pip install --upgrade pip

    echo Installing requirements ...
    $PYCMD -m pip install -r ../requirements.txt

    echo ""
    echo ""
    echo "Installation for Python 3.10 complete!"
else
    echo "Python 3.10 not found!"
fi

sleep 3

