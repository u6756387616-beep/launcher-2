\
@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" "main.py"
) else (
  echo Najpierw uruchom install_and_run.bat albo zbuduj EXE przez build_windows.bat.
  pause
)
