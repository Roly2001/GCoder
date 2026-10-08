# -*- coding: utf-8 -*-
"""
Construye GCoder.exe.

Incluye un parche para un bug de CPython 3.10.0 (corregido en 3.10.1) en
dis._unpack_opargs: al rama 'else' le falta reiniciar extended_arg, asi que un
EXTENDED_ARG seguido de una instruccion sin argumento contamina la siguiente.
PyInstaller lo golpea al analizar bottle.py (dependencia de pywebview) y aborta
con "IndexError: tuple index out of range".

El parche solo se aplica si se detecta el bug, y solo dentro de este proceso.
"""

import dis
import inspect
import os
import shutil
import sys


def _tiene_bug_extended_arg():
    """True si este Python arrastra el bug de dis._unpack_opargs."""
    if sys.version_info[:3] >= (3, 10, 1):
        return False
    try:
        fuente = inspect.getsource(dis._unpack_opargs)
    except (OSError, TypeError):
        return False
    # En la version corregida, la rama 'else' reinicia extended_arg.
    rama_else = fuente.split("else:")[-1]
    return "extended_arg = 0" not in rama_else


def _unpack_opargs_corregido(code):
    extended_arg = 0
    for i in range(0, len(code), 2):
        op = code[i]
        if op >= dis.HAVE_ARGUMENT:
            arg = code[i + 1] | extended_arg
            extended_arg = (arg << 8) if op == dis.EXTENDED_ARG else 0
        else:
            arg = None
            extended_arg = 0  # <-- la linea que falta en 3.10.0
        yield (i, op, arg)


def main():
    if _tiene_bug_extended_arg():
        dis._unpack_opargs = _unpack_opargs_corregido
        print("[build] Python %s: aplicado el parche de dis._unpack_opargs."
              % ".".join(map(str, sys.version_info[:3])))
    else:
        print("[build] Python sin el bug de dis; no hace falta parche.")

    # OJO: en modo carpeta, PyInstaller BORRA la carpeta de destino antes de
    # escribir. Si se le apuntara directamente a la del programa se llevaria
    # por delante Proyectos/ y todo lo demas. Por eso se construye aparte y
    # despues se copian a mano solo las dos cosas que produce: el .exe y su
    # carpeta _internal.
    sys.argv = [
        "pyinstaller", "--noconfirm",
        "--distpath", "./dist",
        "--workpath", "./build",
        "GCoder.spec",
    ]
    from PyInstaller.__main__ import run
    run()

    _colocar()


def _colocar():
    """Lleva el .exe y su _internal a la carpeta del programa."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    salida = os.path.join(aqui, "dist", "GCoder")
    destino = os.path.abspath(os.path.join(aqui, ".."))

    exe = os.path.join(salida, "GCoder.exe")
    interno = os.path.join(salida, "_internal")
    if not os.path.isfile(exe) or not os.path.isdir(interno):
        print("[build] ERROR: no encuentro %s o su _internal" % exe)
        return 1

    viejo = os.path.join(destino, "_internal")
    if os.path.isdir(viejo):
        shutil.rmtree(viejo)
    shutil.copytree(interno, viejo)
    shutil.copy2(exe, os.path.join(destino, "GCoder.exe"))

    n = sum(len(f) for _, _, f in os.walk(viejo))
    print("[build] Colocado: GCoder.exe + _internal (%d archivos) en %s" % (n, destino))
    return 0


if __name__ == "__main__":
    main()
