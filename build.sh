#!/bin/bash
echo "============================================"
echo "  Building AccessBank Desktop App"
echo "============================================"
echo

echo "Step 1: Installing dependencies..."
pip install pyinstaller psycopg2-binary PyQt5 python-docx
echo

echo "Step 2: Building executable..."
pyinstaller AccessBank.spec --clean
echo

if [ -f "dist/AccessBank" ]; then
    echo "============================================"
    echo "  SUCCESS!"
    echo "  Your app is ready at: dist/AccessBank"
    echo "  Share that file with anyone."
    echo "============================================"
else
    echo "============================================"
    echo "  BUILD FAILED - check the errors above"
    echo "============================================"
fi
