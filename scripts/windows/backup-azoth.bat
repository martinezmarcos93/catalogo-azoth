@echo off
chcp 65001 >nul
rem Backup de Azoth (base + portadas + PDFs). Se puede correr con el sistema abierto.
rem Sin nada: guarda en Documentos\Backups-Azoth.
rem Para un pendrive: arrastrar la letra o correr "backup-azoth.bat E:\"
cd /d "%~dp0..\.."
if "%~1"=="" (
  .venv\Scripts\python.exe scripts\crear_backup.py
) else (
  .venv\Scripts\python.exe scripts\crear_backup.py "%~1"
)
pause
