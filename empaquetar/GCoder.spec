# -*- mode: python ; coding: utf-8 -*-
"""Receta de empaquetado de GCoder. Reconstruir con: python construir.py

Se empaqueta en modo CARPETA (onedir), no en un solo archivo.

El motivo no es tecnico sino practico: un .exe onefile se descomprime a si
mismo en una carpeta temporal cada vez que arranca, y ese es justo el
comportamiento que disparan las heuristicas de los antivirus. El GCoder.exe
onefile, sin firmar, lo borro el antivirus de la otra maquina del taller al
descomprimir el zip, y sin avisar. En onedir el ejecutable es un lanzador
normal con sus DLL al lado, que es lo que un antivirus espera ver.

El precio es una carpeta `_internal` junto al .exe. No se toca ni se mueve.
"""

import os

PROYECTO = os.path.abspath(os.path.join(os.getcwd(), ".."))

a = Analysis(
    [os.path.join(PROYECTO, "app.py")],
    pathex=[PROYECTO],          # para que encuentre servidor.py
    binaries=[],
    datas=[
        (os.path.join(PROYECTO, "hub.html"), "."),
        (os.path.join(PROYECTO, "programas.json"), "."),
        # El logotipo de la barra y de la cabecera. Va tambien empaquetado por
        # si alguien mueve el .exe sin llevarse el png al lado.
        (os.path.join(PROYECTO, "logotipo.png"), "."),
    ],
    hiddenimports=["clr", "servidor"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "PIL"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # las DLL van aparte: esto es lo que hace onedir
    name="GCoder",
    # Se genera con: python icono.py
    icon=os.path.join(PROYECTO, "icono.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GCoder",
)
