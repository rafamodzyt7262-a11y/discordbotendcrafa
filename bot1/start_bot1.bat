@echo off
chcp 65001 >nul
title Bot 1 (Kevin 17) - 24/7 Voice Bot
cd /d "%~dp0"

:loop
echo ========================================================
echo   INICIANDO BOT 1 (Kevin 17) - 24/7 EN VOZ
echo ========================================================
python bot.py
echo.
echo [%date% %time%] El proceso del bot se ha detenido.
echo Reiniciando automáticamente en 5 segundos...
timeout /t 5 >nul
echo.
goto loop
