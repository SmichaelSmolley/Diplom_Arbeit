@echo off
setlocal
cd /d "%~dp0"
rem ================================================================
rem  Baut FETCH_FETCHER.exe - eine einzelne, portable Datei.
rem  Laeuft auf jedem Windows-10/11-PC (64 bit) ohne Python-Installation.
rem ================================================================

if not exist ".venv\Scripts\python.exe" (
    echo .venv fehlt - wird zuerst mit setup_venv.bat erstellt ...
    call setup_venv.bat nopause
)

echo === PyInstaller installieren / aktualisieren ===
".venv\Scripts\python.exe" -m pip install --upgrade pyinstaller
if errorlevel 1 goto fehler

echo === Pakete aus requirements.txt sicherstellen ===
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fehler

echo === .exe bauen (dauert 1-3 Minuten) ===
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean ^
    --onefile --windowed ^
    --name FETCH_FETCHER ^
    --collect-data customtkinter ^
    --add-data "qt_theme.json;." ^
    --add-data "winxp.json;." ^
    --add-data "win7.json;." ^
    --add-data "win95.json;." ^
    main.py
if errorlevel 1 goto fehler

copy /Y "dist\FETCH_FETCHER.exe" "FETCH_FETCHER.exe" >nul
echo.
echo ================================================================
echo  Fertig:  %CD%\FETCH_FETCHER.exe
echo  Diese eine Datei auf USB-Stick / anderen PC kopieren und starten.
echo  Retro-Design:  FETCH_FETCHER.exe --retro
echo ================================================================
pause
exit /b 0

:fehler
echo.
echo FEHLER beim Bauen - siehe Meldungen oben.
pause
exit /b 1
