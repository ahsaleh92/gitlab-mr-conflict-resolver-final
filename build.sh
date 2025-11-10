#!/bin/bash
# Build script for GitLab MR Conflict Resolver

echo "========================================"
echo "Building GitLab MR Conflict Resolver"
echo "========================================"
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous build
echo ""
echo "Cleaning previous build..."
rm -rf build/ dist/

# Build executable
echo ""
echo "Building executable..."
python -m PyInstaller build.spec --noconfirm

# Check if build succeeded
if [ -f "dist/MR_Conflict_Resolver_GUI.exe" ]; then
    size=$(du -h "dist/MR_Conflict_Resolver_GUI.exe" | awk '{print $1}')
    echo ""
    echo "========================================"
    echo "✓ Build successful!"
    echo "========================================"
    echo "Output: dist/MR_Conflict_Resolver_GUI.exe"
    echo "Size: $size"
    echo ""
    echo "To run: ./dist/MR_Conflict_Resolver_GUI.exe"
else
    echo ""
    echo "========================================"
    echo "✗ Build failed!"
    echo "========================================"
    exit 1
fi
