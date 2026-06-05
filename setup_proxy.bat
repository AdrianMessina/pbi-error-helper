@echo off
REM Configura el proxy YPF para esta sesion de CMD
REM Ejecutar antes de `pip install -r requirements.txt`
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure
echo Proxy configurado: %HTTPS_PROXY%
