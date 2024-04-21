@echo off
setlocal enabledelayedexpansion

REM PYTHON 3.9 INSTALLATION
cd PY39
call install_py39.cmd
cd ..

REM PYTHON 3.10 INSTALLATION
cd PY310
call install_py310.cmd
cd ..

REM PYTHON 3.11 INSTALLATION
cd PY311
call install_py311.cmd
cd ..

echo.
echo.
echo Installation complete!
timeout /t -1
