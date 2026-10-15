@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 PUBLIER_GITHUB.py
) else (
    python PUBLIER_GITHUB.py
)
echo.
pause
