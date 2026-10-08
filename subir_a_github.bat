@echo off
title SUBIENDO BOTS A GITHUB - RAFA
color 0b
cd /d "%~dp0"
echo ====================================================================
echo        SUBIENDO LOS 4 BOTS A TU REPOSITORIO GITHUB
echo        https://github.com/rafamodzyt7262-a11y/discordbotendcrafa
echo ====================================================================
echo.
git remote remove origin 2>nul
git remote add origin https://github.com/rafamodzyt7262-a11y/discordbotendcrafa.git
git branch -M main
echo Subiendo archivos...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ====================================================================
    echo   EXITO! Todo el proyecto esta en tu GitHub!
    echo   Ahora ve a tu pestana de Railway.com y dale a 'Deploy from GitHub'
    echo ====================================================================
) else (
    echo Hubo un error al subir.
)
pause
