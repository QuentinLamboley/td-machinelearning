@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 launch.py
    goto :fin
)
where python >nul 2>nul
if not errorlevel 1 (
    python launch.py
    goto :fin
)
echo Python introuvable. Installez Python 3.10 a 3.13 depuis python.org.
:fin
echo.
echo Si une erreur est affichee ci-dessus, corrigez-la puis relancez le TD.
pause
