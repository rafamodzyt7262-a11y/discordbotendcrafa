@echo off
chcp 65001 >nul
title Iniciador Maestro - 2 Bots 24/7
echo ========================================================
echo   INICIANDO AMBOS BOTS EN VENTANAS INDEPENDIENTES
echo ========================================================
echo.
echo Iniciando Bot 1 (Kevin 17)...
start "Bot 1 - Kevin 17 (24/7)" cmd /c "cd /d "%~dp0bot1" && start_bot1.bat"

timeout /t 2 >nul

echo Iniciando Bot 2 (RafaModzYT)...
start "Bot 2 - RafaModzYT (24/7)" cmd /c "cd /d "%~dp0bot2" && start_bot2.bat"

echo.
echo ========================================================
echo ¡Ambos bots han sido iniciados con reinicio automático!
echo Puedes cerrar esta ventana. Las ventanas de los bots
echo permanecerán abiertas 24/7.
echo ========================================================
timeout /t 5
