@echo off
chcp 65001 >nul
rem Cambia la contrasena de Azoth si Silvio se la olvido. No borra datos.
cd /d "%~dp0..\.."
.venv\Scripts\python.exe scripts\resetear_clave.py
pause
