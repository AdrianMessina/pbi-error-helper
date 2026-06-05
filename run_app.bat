@echo off
REM PBI Error Helper - Launcher
REM YPF / DA&IA

setlocal

cd /d "%~dp0"

echo ========================================
echo   PBI Error Helper
echo   YPF - Gerencia Visualizacion - DA^&IA
echo ========================================
echo.

REM Setup proxy
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure

REM Create venv if missing
if not exist "venv\" (
    echo [*] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install deps if streamlit missing
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [*] Instalando dependencias ^(primera ejecucion^)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
)

echo.
echo [*] Iniciando PBI Error Helper...
echo [*] El navegador se abrira automaticamente.
echo.
echo Presiona Ctrl+C para detener.
echo ========================================
echo.

streamlit run app.py

endlocal
