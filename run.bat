@echo off
rem WARP portable launcher (Windows)
rem Double-click to start, then open http://127.0.0.1:8300 in your browser.
rem NOTE: keep this file ASCII-only (cmd.exe parses it with the OEM codepage).
cd /d "%~dp0"

rem --- find a Python that has NiceGUI installed ---
set "PYEXE="
python -c "import nicegui" >nul 2>nul && set "PYEXE=python"
if not defined PYEXE (
    py -3 -c "import nicegui" >nul 2>nul && set "PYEXE=py -3"
)
if not defined PYEXE (
    echo [ERROR] No Python with NiceGUI found.
    echo         Install dependencies first:  pip install -r requirements.txt
    pause
    exit /b 1
)

%PYEXE% warp_web.py
if errorlevel 1 (
    echo.
    echo [ERROR] warp_web.py exited with an error. Check the messages above.
    pause
)
