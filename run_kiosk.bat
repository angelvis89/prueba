@echo off
REM Comprueba dependencias e inicia el kiosco
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python no esta instalado. Instale Python 3 y vuelva a ejecutar este script.
    pause
    exit /b 1
)

REM Asegurar que pip este disponible
python -m ensurepip >nul 2>&1

REM Instalar modulo keyboard si no existe
python -c "import importlib,sys; sys.exit(0 if importlib.util.find_spec('keyboard') else 1)" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Instalando dependencia keyboard...
    pip install keyboard
)

python kiosk_app.py
