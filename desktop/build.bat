@echo off
echo ============================================
echo   Building AccessBank Desktop App
echo ============================================
echo.

echo Step 1: Installing dependencies...
pip install pyinstaller psycopg2-binary PyQt5 python-docx
echo.

echo Step 2: Building executable...
python -m PyInstaller AccessBank.spec --clean
echo.

if exist "dist\AccessBank.exe" (
    echo ============================================
    echo   SUCCESS!
    echo   Your app is ready at: dist\AccessBank.exe
    echo   Share that file with anyone.
    echo ============================================
) else (
    echo ============================================
    echo   BUILD FAILED - check the errors above
    echo ============================================
)

pause
