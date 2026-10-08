# -*- coding: utf-8 -*-
"""Arranca GCoder sin el .exe: el servidor y el navegador que ya tienes.

Sirve para maquinas donde el antivirus se lleve el ejecutable. Dentro de
GCoder.exe esto lo hace app.py.

    python servir.py [puerto] [--sin-navegador]

El navegador lo abre ESTE archivo, no el .bat que lo llama. Antes lo abria el
.bat justo antes de arrancar el servidor y llegaba primero, asi que la primera
carga fallaba con un error de localhost. Aqui el socket ya esta escuchando
—ThreadingHTTPServer se ata en su constructor— cuando se abre.

NO HACE FALTA INTERNET. Todo se sirve desde esta carpeta: los programas son un
solo archivo HTML cada uno, sin CDN, sin fuentes de fuera y sin llamadas de red.
"""

import json
import os
import socket
import sys
import urllib.request
import webbrowser

import servidor


def _ocupado(puerto):
    """Hay algo escuchando en ese puerto.

    Hace falta mirarlo A MANO: en Windows, HTTPServer pone allow_reuse_address,
    asi que atarse a un puerto ya usado NO da error y acabarias con dos
    servidores compitiendo por el mismo sitio. Comprobado, no supuesto.
    """
    s = socket.socket()
    s.settimeout(0.4)
    try:
        s.connect(("127.0.0.1", puerto))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _es_gcoder(puerto):
    """Lo que ya esta escuchando, es otro GCoder abierto."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/programas.json" % puerto,
                                    timeout=1) as r:
            return "programas" in json.loads(r.read().decode("utf-8"))
    except Exception:
        return False


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    puerto = int(args[0]) if args else 8817
    raiz = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(raiz, "programas.json")

    # Se pregunta UNA vez y se guarda: preguntarlo dos veces puede dar
    # respuestas distintas, porque cada consulta deja una conexion a medias en
    # la cola del otro programa y la siguiente ya no entra.
    ocupado = _ocupado(puerto)

    # Si ya hay un GCoder abierto, no se levanta otro: se abre el que hay.
    if ocupado and _es_gcoder(puerto):
        url = "http://127.0.0.1:%d/" % puerto
        print("")
        print("  GCoder ya estaba abierto en %s" % url)
        print("  Te lo abro en el navegador.")
        print("")
        webbrowser.open(url)
        sys.exit(0)

    # Ocupado por otra cosa: se busca sitio en vez de pelearse por el puerto.
    # Y aun asi se prueba a atarse de verdad: mirar si un puerto responde no
    # garantiza que se pueda usar, asi que manda el intento, no la consulta.
    srv = None
    candidatos = [puerto] if not ocupado else []
    candidatos += list(range(puerto + 1, puerto + 20))
    for p in candidatos:
        try:
            srv, puerto = servidor.iniciar(raiz, ruta_json, p, base=raiz)
            break
        except OSError:
            continue

    if srv is None:
        print("")
        print("  No encontre ningun puerto libre entre el %d y el %d."
              % (puerto, puerto + 19))
        print("  Cierra otros programas que usen la red y vuelve a intentarlo.")
        print("")
        input("  Pulsa Intro para cerrar. ")
        sys.exit(1)

    url = "http://127.0.0.1:%d/" % puerto
    print("")
    print("  GCoder abierto en   %s" % url)
    print("  Deja esta ventana abierta mientras trabajes: es el servidor.")
    print("  Para cerrarlo, Ctrl+C o cierra la ventana.")
    print("")

    if "--sin-navegador" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            print("  No pude abrir el navegador solo. Abre esa direccion a mano.")

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("  Cerrado.")
