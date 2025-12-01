@echo off
echo ============================================================
echo   MEDIA AUTO PUBLISH - Demarrage Keep Alive Service
echo ============================================================
echo.

cd /d "%~dp0"

echo Verification de Python...
python --version
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou non trouve dans PATH
    pause
    exit /b 1
)

echo.
echo Verification des dependances...
pip show schedule >nul 2>&1
if errorlevel 1 (
    echo Installation de la bibliotheque 'schedule'...
    pip install schedule requests
)

echo.
echo Lancement du service Keep-Alive...
echo Appuyez sur Ctrl+C pour arreter
echo.

python keep_alive.py

pause
