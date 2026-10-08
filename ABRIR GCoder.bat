@echo off
rem ---------------------------------------------------------------------
rem  Abre GCoder SIN el .exe.
rem
rem  Sirve para las maquinas donde el antivirus o la politica de la empresa
rem  bloquean los ejecutables: aqui no hay ninguno, solo Python arrancando
rem  el servidor y el navegador que ya tiene Windows.
rem
rem  NO HACE FALTA INTERNET: todo se sirve desde esta carpeta.
rem
rem  El navegador lo abre servir.py cuando el servidor YA esta escuchando.
rem  Abrirlo desde aqui antes daba un error de localhost, porque llegaba
rem  primero.
rem ---------------------------------------------------------------------
cd /d "%~dp0"
title GCoder

where python >nul 2>nul
if errorlevel 1 goto sinpython

python servir.py 8817
goto fin

:sinpython
echo.
echo   No encuentro Python en esta computadora.
echo.
echo   ESTE ARCHIVO SOLO HACE FALTA SI NO PUEDES USAR EL .EXE.
echo.
echo     1) Prueba primero GCoder.exe, que esta en esta misma
echo        carpeta. No necesita Python ni instalar nada.
echo.
echo     2) Si el antivirus se llevo el .exe, instala Python desde
echo        python.org (marca "Add to PATH") y vuelve a ejecutar
echo        este archivo. Asi funciona todo, Proyectos incluidos.
echo.
echo     3) Y si no puedes ni una cosa ni la otra, abre los programas
echo        sueltos: entra en la carpeta "programas" y abre con el
echo        navegador el .html de version mas alta de cada uno.
echo        Miden, dibujan y generan G-code igual; lo que guardes
echo        ira a Descargas.
echo.
echo        OJO: hub.html NO se abre asi. Esa pantalla necesita el
echo        servidor; si la abres sola, te lo dira ella misma.
echo.
pause

:fin
