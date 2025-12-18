@echo off
set "WORKDIR=%~dp0"
cd /d "%WORKDIR%"

echo Iniciando TTS Local - Modo Batch...
echo La aplicacion estara disponible en http://localhost:5001

:: Abrir el navegador despues de un breve delay
start "" "http://localhost:5001"

:: Ejecutar la aplicacion Flask
python app.py

pause
