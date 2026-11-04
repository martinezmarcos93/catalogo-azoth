@echo off
chcp 65001 >nul
rem Arranca Azoth. Esta ventana tiene que quedar abierta (se puede minimizar):
rem si se cierra, el sistema deja de andar en la PC y en el celular.
title Azoth - no cerrar esta ventana
cd /d "%~dp0..\.."
if not exist .venv\Scripts\python.exe (
  echo Falta instalar. Correr primero scripts\windows\instalar-azoth.bat
  pause
  exit /b 1
)
.venv\Scripts\python.exe -u run.py
pause
