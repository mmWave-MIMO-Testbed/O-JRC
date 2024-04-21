#!/bin/bash

# PYTHON 3.11 INSTALLATION
if py311="$(python3.11 -V 2>&1)"; then
    echo "Python 3.11 found!"
    PYCMD=python3.11

    $PYCMD -m pip install --upgrade pip

    echo Installing requirements ...
    $PYCMD -m pip install -r ../requirements.txt

    echo ""
    echo ""
    echo "Installation for Python 3.11 complete!"
else
    echo "Python 3.11 not found!"
fi

sleep 3

