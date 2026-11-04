@echo off
chcp 65001 >nul
rem Instala Azoth: crea el entorno de Python e instala lo necesario.
rem Se corre UNA sola vez (y de nuevo despues de actualizar el sistema).
cd /d "%~dp0..\.."
where py >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python. Instalarlo desde https://www.python.org/downloads/ y volver a correr esto.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Hubo un error instalando. Revisar la conexion a internet y volver a correr.
  pause
  exit /b 1
)
echo.
echo Listo. Para abrir el sistema: doble clic en scripts\windows\iniciar-azoth.bat
pause
