@echo off
REM install_dependencies.bat
REM Setup script for the ShipIt project (Windows)
REM ---------------------------------------------------
REM 1. Backend  – uses Conda if available, otherwise falls back to pip.
REM 2. Front-end – installs React-Native / Expo packages with npm.

SETLOCAL ENABLEDELAYEDEXPANSION

ECHO ================================
ECHO Installing backend dependencies
ECHO ================================

WHERE conda >NUL 2>NUL
IF %ERRORLEVEL% == 0 (
    ECHO Conda detected. Creating/updating environment "shipit" from config\environment.yml
    REM Attempt to create env; if it exists, update it.
    conda env create -f config\environment.yml 2>NUL
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Environment already exists. Updating packages...
        conda env update -f config\environment.yml
    ) ELSE (
        ECHO Environment created. Activate with: conda activate shipit
    )
) ELSE (
    ECHO Conda not detected. Falling back to system Python + pip.
    python -m pip install --upgrade pip
    python -m pip install -r config\requirements.txt
)

ECHO.
ECHO ================================
ECHO Installing mobile dependencies
ECHO ================================

IF EXIST mobile (
    CD mobile
    WHERE npm >NUL 2>NUL
    IF %ERRORLEVEL% == 0 (
        npm install --legacy-peer-deps
    ) ELSE (
        ECHO npm is required but not found. Please install Node.js and npm, then re-run this script.
        GOTO :EOF
    )
    CD ..
) ELSE (
    ECHO Mobile directory not found! Skipping front-end setup.
)

ECHO.
ECHO ✅  All dependencies installed. Happy hacking!

ENDLOCAL 