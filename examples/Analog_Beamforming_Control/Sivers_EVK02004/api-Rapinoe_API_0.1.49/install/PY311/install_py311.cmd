@echo off
setlocal enabledelayedexpansion

REM PYTHON 3.11 INSTALLATION
py -3.11 --version > ~tmp
SET FOUND=0
echo %%G | findstr /b /c:"Python 3.11." ~tmp >nul && set FOUND=1
if !FOUND!==1 (
    echo Python 3.11 found!
    set PYCMD=py -3.11

    !PYCMD! -m pip install --upgrade pip

    echo Installing requirements ...
    !PYCMD! -m pip install -r ../requirements.txt

    echo.
    echo.
    echo Installation for Python 3.11 complete!
)

del ~tmp
timeout /t 3
