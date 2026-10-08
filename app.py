# -*- coding: utf-8 -*-
"""
GCoder - hub de programas.

Abre una ventana nativa con pestanas. Cada pestana carga uno de tus
programas HTML, que siguen viviendo en su propia carpeta: aqui solo se
apuntan desde programas.json.

Todo se sirve por http://127.0.0.1 (no file://) porque es la unica forma
de que el hub pueda comunicarse con los programas que carga en iframes.
"""

import base64
import os
import sys

import webview

import servidor

TITULO = "GCoder"


def _dir_app():
    """Carpeta donde vive el .exe (o este script)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _dir_paquete():
    """Carpeta de recursos empaquetados dentro del .exe."""
    return getattr(sys, "_MEIPASS", _dir_app())


def recurso(nombre):
    """Prefiere el archivo que este junto al .exe; si no, el empaquetado.

    Asi puedes editar hub.html o programas.json sin reconstruir nada.
    """
    fuera = os.path.join(_dir_app(), nombre)
    if os.path.isfile(fuera):
        return fuera
    return os.path.join(_dir_paquete(), nombre)


class Api(object):
    """Puente expuesto al JS como window.pywebview.api"""

    def __init__(self):
        self._window = None            # el guion bajo evita que pywebview lo serialice
        self._last_dir = _dir_app()

    def save_file(self, payload):
        payload = payload or {}
        nombre = payload.get("name") or "archivo.txt"
        b64 = payload.get("b64") or ""
        # El hub manda la carpeta del proyecto abierto: el dialogo se abre ahi
        # en vez de en "la ultima que usaste", que casi nunca es la que quieres.
        sugerida = payload.get("dir") or ""

        try:
            datos = base64.b64decode(b64)
        except Exception as exc:
            return {"saved": False, "error": "base64: %s" % exc}

        if sugerida and os.path.isdir(sugerida):
            inicio = sugerida
        elif os.path.isdir(self._last_dir):
            inicio = self._last_dir
        else:
            inicio = _dir_app()
        res = self._window.create_file_dialog(
            webview.SAVE_DIALOG, directory=inicio, save_filename=nombre
        )
        if not res:
            return {"saved": False, "cancelled": True}
        ruta = res[0] if isinstance(res, (list, tuple)) else res

        try:
            with open(ruta, "wb") as fh:
                fh.write(datos)
        except Exception as exc:
            return {"saved": False, "error": str(exc)}

        self._last_dir = os.path.dirname(ruta)
        return {"saved": True, "path": ruta}


def _informe(ruta_json):
    lineas = ["GCoder - diagnostico", "--------------------",
              "Carpeta del programa : %s" % _dir_app(),
              "hub.html             : %s" % recurso("hub.html"),
              "programas.json       : %s" % ruta_json, ""]
    try:
        datos = servidor.leer_manifiesto(ruta_json)
    except Exception as exc:
        lineas.append("ERROR leyendo programas.json: %s" % exc)
        return "\n".join(lineas)

    for p in datos.get("programas", []):
        lineas.append("[%s] %s" % (p.get("id"), p.get("nombre")))
        lineas.append("    configurada : %s" % (p.get("carpeta_configurada") or "(sin definir)"))
        lineas.append("    resuelta    : %s" % (p.get("carpeta") or "(sin definir)"))
        lineas.append("    archivo  : %s" % (p.get("archivo_resuelto") or "(ninguno)"))
        lineas.append("    estado   : %s" % ("disponible" if p.get("disponible") else "no disponible"))
        if p.get("problema"):
            lineas.append("    PROBLEMA : %s" % p["problema"])
    return "\n".join(lineas) + "\n"


def main():
    ruta_json = recurso("programas.json")
    raiz = os.path.dirname(recurso("hub.html"))

    # Uso:  GCoder.exe --info [salida.txt]
    if "--info" in sys.argv:
        texto = _informe(ruta_json)
        i = sys.argv.index("--info")
        destino = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        if destino:
            with open(destino, "w", encoding="utf-8") as fh:
                fh.write(texto)
        else:
            sys.stdout.write(texto)
        return 0

    # La ventana es WebView2, y WebView2 obedece al proxy del sistema. En una
    # maquina de taller con proxy configurado y SIN internet, eso rompe hasta
    # http://127.0.0.1: el navegador intenta salir por un proxy que no
    # responde y sale un error de localhost. Como aqui nunca se pide nada
    # fuera de esta maquina, se le dice que no use proxy ninguno y que no haga
    # llamadas de fondo. Hay que ponerlo ANTES de crear la ventana.
    os.environ.setdefault(
        "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
        "--no-proxy-server --disable-background-networking "
        "--disable-component-update --no-first-run",
    )

    # Los proyectos van SIEMPRE junto al .exe, nunca en la carpeta temporal
    # de la que salen los recursos empaquetados.
    _srv, puerto = servidor.iniciar(raiz, ruta_json, base=_dir_app())

    api = Api()
    ventana = webview.create_window(
        TITULO,
        url="http://127.0.0.1:%d/hub.html" % puerto,
        js_api=api,
        width=1500,
        height=950,
        min_size=(1000, 640),
        text_select=True,
    )
    api._window = ventana

    webview.start(debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
