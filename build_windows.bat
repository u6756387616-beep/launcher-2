@echo off
setlocal
cd /d "%~dp0"
title LOK LAUNCHER - BUILD

echo.
echo  LOK LAUNCHER - BUILD WINDOWS APP
echo  --------------------------------
echo.
echo Ten skrypt sluzy tylko do BUDOWANIA instalatora.
echo Gotowy LOK Launcher nie wymaga Pythona na komputerze gracza.
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [INFO] Brak Pythona na komputerze budujacym.
  echo Do zbudowania EXE uzyj GitHub Actions zgodnie z BUILD_WITHOUT_LOCAL_PYTHON.md.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto error

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

python -m pip install --upgrade pip
if errorlevel 1 goto error

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error

python -m PyInstaller --noconfirm --clean --windowed --onedir ^
  --name "LOK Launcher" ^
  --add-data "assets;assets" ^
  --collect-all minecraft_launcher_lib ^
  main.py
if errorlevel 1 goto error

if exist "installer_output" rmdir /s /q "installer_output"
mkdir "installer_output"

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo [BLAD] Nie znaleziono Inno Setup 6.
  echo Zainstaluj Inno Setup 6 albo uzyj GitHub Actions.
  pause
  exit /b 1
)

"%ISCC%" "installer.iss"
if errorlevel 1 goto error

echo.
echo [OK] GOTOWE!
echo Instalator: installer_output\LOK_Launcher_Setup_0.3.0.exe
echo Ten plik mozna uruchomic bez instalowania Pythona.
echo.
pause
exit /b 0

:error
echo.
echo [BLAD] Budowanie nie powiodlo sie. Sprawdz komunikat powyzej.
pause
exit /b 1
