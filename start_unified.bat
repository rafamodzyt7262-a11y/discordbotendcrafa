@echo off
chcp 65001 >nul
title Bots 24/7 (Kevin 17 & RafaModzYT) - Unificado
cd /d "%~dp0"

:loop
echo ========================================================
echo   INICIANDO AMBOS BOTS 24/7 EN UNA SOLA CONSOLA
echo ========================================================
python run_both_unified.py
echo.
echo [%date% %time%] El proceso se ha detenido.
echo Reiniciando automáticamente en 5 segundos...
timeout /t 5 >nul
echo.
goto loop
