@echo off
cd /d "%~dp0"
echo.
echo  Reconstruyendo GCoder.exe ...
echo.
python construir.py
if errorlevel 1 (
  echo.
  echo  *** FALLO el empaquetado. Revisa los mensajes de arriba. ***
  pause
  exit /b 1
)
echo.
echo  Listo: ..\GCoder.exe
echo.
pause
