@echo off
setlocal

cd /d "%~dp0"

title Quiz Helper Build Tool

echo ======================================================
echo              Quiz Helper Build
echo ======================================================
echo.
echo [Status] Cleaning old build cache...
if exist build rd /s /q build

set "ICON_FILE="
set "ICON_NAME="
set "ICON_TEMP=%TEMP%\quiz_helper_icon_path.txt"

if exist "%ICON_TEMP%" del /q "%ICON_TEMP%" >nul 2>nul
if exist "%CD%\logo\*.ico" (
    dir /b /a-d /on "%CD%\logo\*.ico" > "%ICON_TEMP%"
    set /p ICON_NAME=<"%ICON_TEMP%"
)
if exist "%ICON_TEMP%" del /q "%ICON_TEMP%" >nul 2>nul
if defined ICON_NAME set "ICON_FILE=%CD%\logo\%ICON_NAME%"

if defined ICON_FILE (
    echo [Status] Icon found: %ICON_FILE%
) else (
    echo [Info] No .ico file found in logo folder. Default icon will be used.
)

echo [Status] Starting PyInstaller with uv...
echo.

if defined ICON_FILE (
    uv run --with pyinstaller python -m PyInstaller --noconsole --onefile --icon "%ICON_FILE%" --name "QuizHelper" main.py
) else (
    uv run --with pyinstaller python -m PyInstaller --noconsole --onefile --name "QuizHelper" main.py
)

echo.
if %errorlevel% neq 0 (
    echo [Error] Build failed. Please check the messages above.
) else (
    echo [OK] Build complete. The exe is in the dist folder.
)

echo.
pause
