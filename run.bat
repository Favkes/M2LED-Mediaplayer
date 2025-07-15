@echo off

REM Navigate to the project directory:
cd /d "%~dp0"

REM Activate venv
call .venv/Scripts/activate.bat

REM Run the main script and save logs
python main.py

REM Keep window open after exit
pause
