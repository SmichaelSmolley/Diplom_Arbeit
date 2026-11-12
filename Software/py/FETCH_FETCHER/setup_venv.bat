@echo off
setlocal
cd /d "%~dp0"

echo === Virtuelle Umgebung erstellen (.venv) ===
rem Bevorzugt Python 3.12 ueber den py-Launcher, sonst das normale "python" (z. B. 3.11)
set "PY=python"
py -3.12 --version >nul 2>&1
if %errorlevel%==0 set "PY=py -3.12"
echo Verwende: %PY%
%PY% --version

if exist ".venv\Scripts\python.exe" (
    echo .venv existiert bereits - wird weiterverwendet.
) else (
    %PY% -m venv .venv
    if errorlevel 1 (
        echo FEHLER: venv konnte nicht erstellt werden. Ist Python installiert und im PATH?
        pause
        exit /b 1
    )
)

echo === pip aktualisieren ===
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo === Pakete aus requirements.txt installieren ===
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo FEHLER bei der Installation der Pakete.
    pause
    exit /b 1
)

echo.
echo Fertig! Aktivieren mit:  .venv\Scripts\activate
echo Starten mit:            .venv\Scripts\python.exe main.py
if /i not "%~1"=="nopause" pause
endlocal
