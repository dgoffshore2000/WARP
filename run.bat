@echo off
setlocal enabledelayedexpansion
rem WARP portable launcher (Windows)
rem Priority: Anaconda / Miniconda python -> system python -> py launcher.
rem Double-click to start, then open http://127.0.0.1:8300 in your browser.
rem NOTE: keep this file ASCII-only (cmd.exe parses it with the OEM codepage).
cd /d "%~dp0"

set "PYEXE="

rem --- 1) common Anaconda / Miniconda install locations ---
for %%D in (
    "C:\ProgramData\anaconda3"
    "%USERPROFILE%\anaconda3"
    "%USERPROFILE%\miniconda3"
    "%USERPROFILE%\Anaconda3"
    "%LOCALAPPDATA%\anaconda3"
    "%LOCALAPPDATA%\Continuum\anaconda3"
) do (
    if not defined PYEXE if exist "%%~D\python.exe" (
        "%%~D\python.exe" -c "import nicegui" >nul 2>nul && set "PYEXE=%%~D\python.exe"
    )
)

rem --- 2) conda base env, if conda is on PATH ---
if not defined PYEXE (
    for /f "usebackq delims=" %%B in (`conda info --base 2^>nul`) do (
        if not defined PYEXE if exist "%%B\python.exe" (
            "%%B\python.exe" -c "import nicegui" >nul 2>nul && set "PYEXE=%%B\python.exe"
        )
    )
)

rem --- 3) fallback: python on PATH, then py launcher ---
if not defined PYEXE (
    python -c "import nicegui" >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
    py -3 -c "import nicegui" >nul 2>nul && set "PYEXE=py -3"
)

if not defined PYEXE (
    echo [ERROR] No Python with NiceGUI found.
    echo         Install Anaconda, or run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Using Python: %PYEXE%
echo Starting WARP Web on http://127.0.0.1:8300  --  press Ctrl+C to stop
echo.
%PYEXE% warp_web.py
if errorlevel 1 (
    echo.
    echo [ERROR] warp_web.py exited with an error. Check the messages above.
    pause
)
