#!/bin/bash

sudo cp 11-ftdi.rules /etc/udev/rules.d/

# PYTHON 3.9 INSTALLATION
cd PY39
./install_py39.sh
cd ..

# PYTHON 3.10 INSTALLATION
cd PY310
./install_py310.sh
cd ..

# PYTHON 3.11 INSTALLATION
cd PY311
./install_py311.sh
cd ..

echo ""
echo ""
echo "Installation complete!"
sleep 3

