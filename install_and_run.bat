@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ nie zostal znaleziony. Zainstaluj Python z python.org.
  pause
  exit /b 1
)
if not exist .venv py -m venv .venv
call .venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py main.py
if errorlevel 1 pause
