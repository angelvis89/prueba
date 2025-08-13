@echo off
REM Comprueba dependencias y envia reactivacion
IF "%1"=="" (
    echo Uso: run_remote_activate.bat ^<IP del kiosco^>
    exit /b 1
)

python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python no esta instalado. Instale Python 3 y vuelva a ejecutar este script.
    pause
    exit /b 1
)

python -m ensurepip >nul 2>&1

REM Instalar modulo requests si no existe
python -c "import importlib,sys; sys.exit(0 if importlib.util.find_spec('requests') else 1)" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Instalando dependencia requests...
    pip install requests
)

python remote_activate.py %1
