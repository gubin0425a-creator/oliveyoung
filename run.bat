@echo off
title K-Beauty Global Lister Server
cd /d "%~dp0"
echo Starting K-Beauty Global Lister Server...
call .venv\Scripts\activate.bat
python app.py
pause
