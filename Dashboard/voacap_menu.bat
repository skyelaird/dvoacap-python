@echo off
REM VE1ATM Propagation System - VOACAP Setup and Usage
REM ====================================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  VE1ATM HF Propagation - VOACAP Accurate Mode Setup        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:MENU
echo.
echo What would you like to do?
echo.
echo   1. Install VOACAP (one-time setup)
echo   2. Generate Quick predictions (ITU-R - Fast)
echo   3. Generate Accurate predictions (VOACAP - Slow but accurate)
echo   4. Start web server
echo   5. Exit
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto QUICK
if "%choice%"=="3" goto VOACAP
if "%choice%"=="4" goto SERVER
if "%choice%"=="5" goto END
goto MENU

:INSTALL
echo.
echo Installing pythonprop (VOACAP wrapper)...
echo This may take a few minutes...
echo.
pip install pythonprop
echo.
echo Testing installation...
python -c "import pythonprop; print('✓ VOACAP installed successfully!')"
if %errorlevel% neq 0 (
    echo.
    echo ⚠ Installation failed. Make sure Python and pip are installed.
    echo   Try: python -m pip install --upgrade pip
    echo   Then: pip install pythonprop
    pause
) else (
    echo.
    echo ✓ VOACAP is ready to use!
    echo   You can now run Accurate predictions (option 3)
    pause
)
goto MENU

:QUICK
echo.
echo Generating Quick predictions (ITU-R model)...
echo This will take 2-3 seconds...
echo.
python generate_propagation_voacap.py
if %errorlevel% equ 0 (
    echo.
    echo ✓ Quick predictions generated!
    echo   Refresh your browser to see updated data
) else (
    echo.
    echo ⚠ Error generating predictions
)
pause
goto MENU

:VOACAP
echo.
echo Generating Accurate predictions (VOACAP model)...
echo This will take 30-60 seconds - please wait...
echo.
python generate_propagation_voacap.py --voacap
if %errorlevel% equ 0 (
    echo.
    echo ✓ Accurate VOACAP predictions generated!
    echo   Refresh your browser to see updated data
) else (
    echo.
    echo ⚠ Error: VOACAP not installed or failed
    echo   Run option 1 to install VOACAP first
)
pause
goto MENU

:SERVER
echo.
echo Starting web server on port 8000...
echo.
echo Open your browser to: http://localhost:8000/propagation_dashboard_tabbed.html
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
goto MENU

:END
echo.
echo 73 and Good DX!
echo.
pause
exit
