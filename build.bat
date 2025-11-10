@echo off
REM Build script for GitLab MR Conflict Resolver (Windows)

echo ========================================
echo Building GitLab MR Conflict Resolver
echo ========================================
echo.

REM Check Python version
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    exit /b 1
)

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous build
echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
echo.
echo Building executable...
python -m PyInstaller build.spec --noconfirm

REM Check if build succeeded
if exist "dist\MR_Conflict_Resolver_GUI.exe" (
    echo.
    echo ========================================
    echo Build successful!
    echo ========================================
    echo Output: dist\MR_Conflict_Resolver_GUI.exe
    dir dist\MR_Conflict_Resolver_GUI.exe | findstr "MR_Conflict"
    echo.
    echo To run: dist\MR_Conflict_Resolver_GUI.exe
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    exit /b 1
)
