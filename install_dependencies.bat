@echo off
chcp 65001 >nul
echo ====================================================
echo   INSTALANDO DEPENDENCIAS PARA LOS BOTS DE DISCORD
echo ====================================================
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Dependencias instaladas correctamente.
pause
