@echo off
title Sistema FSM - Taller de Celulares
color 0A
echo ====================================================
echo     INICIANDO SISTEMA FSM PARA MASTERFIX
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/3] Asegurando librerias necesarias (FastAPI, Uvicorn y Multipart)...
python -m pip install fastapi uvicorn sqlalchemy jinja2 python-multipart

echo [2/3] Abriendo el navegador web...
start http://127.0.0.1:8000

echo [3/3] Iniciando servidor local. NO CIERRES ESTA VENTANA...
echo ----------------------------------------------------
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause