# -*- coding: utf-8 -*-
"""
Servidor local de GCoder.

Sirve el hub y cada programa bajo el MISMO origen (http://127.0.0.1:puerto),
que es la unica forma de que el hub pueda comunicarse con los programas que
carga en un iframe. Con file:// el navegador lo prohibe.

Cada programa se monta en /p/<id>/ apuntando a su carpeta real, asi que los
programas se quedan donde ya viven; no hay que moverlos ni copiarlos.
"""

import datetime
import glob
import io
import json
import mimetypes
import os
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("image/svg+xml", ".svg")


def clave_version(ruta):
    """(1, 17) a partir de 'Programa_v1.17.html'. Orden numerico, no alfabetico."""
    m = re.search(r"_v(\d+(?:\.\d+)*)", os.path.basename(ruta))
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)


def elegir_archivo(carpeta, patron):
    """Del patron (p.ej. 'Prog_v*.html') devuelve el nombre de la version mas alta."""
    if not carpeta or not patron:
        return None
    hallados = [p for p in glob.glob(os.path.join(carpeta, patron)) if os.path.isfile(p)]
    if not hallados:
        return None
    hallados.sort(key=lambda p: (clave_version(p), os.path.getmtime(p)))
    return os.path.basename(hallados[-1])


def resolver_carpeta(carpeta, base):
    """Convierte la carpeta del manifiesto en una ruta real.

    Una ruta RELATIVA se resuelve respecto a programas.json. Es lo que hace
    portable el conjunto: se copia a otro equipo, a otro usuario o a otro
    disco y las rutas siguen valiendo, porque no dependen de DONDE esta todo
    sino de COMO estan colocadas las carpetas entre si.

    Se siguen admitiendo rutas absolutas y variables del sistema (%USERPROFILE%)
    por si algun programa vive fuera del conjunto.
    """
    if not carpeta:
        return ""
    carpeta = os.path.expanduser(os.path.expandvars(carpeta))
    if os.path.isabs(carpeta):
        return os.path.normpath(carpeta)
    return os.path.normpath(os.path.join(base, carpeta))


def leer_manifiesto(ruta_json):
    """Lee programas.json y resuelve, para cada programa, su archivo y su URL."""
    with io.open(ruta_json, encoding="utf-8") as fh:
        datos = json.load(fh)

    base = os.path.dirname(os.path.abspath(ruta_json))
    for prog in datos.get("programas", []):
        prog["carpeta_configurada"] = prog.get("carpeta") or ""
        carpeta = resolver_carpeta(prog["carpeta_configurada"], base)
        prog["carpeta"] = carpeta
        archivo = elegir_archivo(carpeta, prog.get("archivo") or "")
        prog["archivo_resuelto"] = archivo
        if archivo and os.path.isdir(carpeta):
            prog["url"] = "/p/" + prog["id"] + "/" + archivo
            prog["disponible"] = True
        else:
            prog["url"] = None
            prog["disponible"] = False
            # Distingue "aun no lo he hecho" de "deberia estar y no aparece".
            if prog.get("estado") == "listo":
                prog["problema"] = (
                    "No se encontro '%s' en %s"
                    % (prog.get("archivo"), carpeta or "(sin carpeta)")
                )
    return datos


# ============================================================== PROYECTOS
#
# Un proyecto es una CARPETA con el nombre de la pieza y, dentro, todo lo que
# esa pieza necesita: la lamina medida, sus recorridos, su contorno, su
# programa de corte. Plano, sin subcarpetas: una pieza tiene cinco o diez
# archivos, y el tipo va en el nombre.
#
# Se eligio por pieza y no por programa porque asi es como se trabaja: la
# Cervical pasa por el disenador, el editor, la soldadura y Origen. Una carpeta
# por programa repartiria una sola pieza en cuatro sitios, que es justo el lio
# que hubo que resolver.

CARPETA_PROYECTOS = "Proyectos"

# Sufijo de archivo -> tipo, para lo que generamos nosotros.
SUFIJOS = {
    "lamina": "lamina",
    "recorrido": "recorrido-soldadura",
    "contorno": "contorno",
    "corte": "corte",
    "coordenadas": "coordenadas",
    "recal": "recalibrado",
}

ETIQUETAS = {
    "lamina": u"Lámina medida",
    "recorrido-soldadura": u"Recorrido de soldadura",
    "contorno": u"Contorno de la pieza",
    "corte": u"Programa de corte",
    "coordenadas": u"Lista de coordenadas",
    "recalibrado": u"Recalibrado",
    "desconocido": u"Sin identificar",
}


def carpeta_proyectos(base):
    return os.path.join(base, CARPETA_PROYECTOS)


def nombre_seguro(nombre, con_punto=False):
    """Deja pasar un nombre de carpeta o de archivo, y nada mas.

    No basta con quitar '..': en Windows tambien hay que cerrar la puerta a
    ':' (unidades y flujos alternativos) y a las barras de cualquier tipo.
    """
    nombre = (nombre or "").strip()
    if not nombre or nombre in (".", ".."):
        return ""
    prohibidos = chr(92) + chr(47) + chr(58) + chr(42) + chr(63) + chr(34) + \
                 chr(60) + chr(62) + chr(124) + chr(13) + chr(10) + chr(9)
    if any(c in nombre for c in prohibidos):
        return ""
    if not con_punto and "." in nombre:
        return ""
    return nombre


def cabecera_taller(texto):
    """Lee la linea de identidad si el archivo la trae.

    ; GCODER v1 tipo=recorrido-soldadura proyecto=Cervical fecha=2026-09-05

    Sin barras verticales a proposito: el lector de laminas parte por '|' y una
    cabecera con barras se colaria como si fuera un circulo.
    """
    for linea in texto.split("\n")[:8]:
        # Se aceptan los nombres anteriores (GFORGE, TALLER): hay archivos
        # ya sellados con ellos y tienen que seguir reconociendose.
        m = re.match(r"^\s*[;#]\s*(?:GCODER|GFORGE|TALLER)\b(.*)$", linea)
        if not m:
            continue
        datos = {}
        for par in re.finditer(r"(\w+)=([^\s]+)", m.group(1)):
            datos[par.group(1)] = par.group(2)
        return datos
    return None


def detectar_tipo(texto, nombre=""):
    """Que es este archivo. Primero lo que el archivo declare; luego, su forma."""
    cab = cabecera_taller(texto)
    if cab and cab.get("tipo"):
        return cab["tipo"]

    # Lo que declare el nombre, si sigue la convencion.
    partes = os.path.basename(nombre).lower().split(".")
    for p in partes[1:-1]:
        # Se le quita lo que distingue una copia de otra: la fecha de la
        # corrida y/o el numero de orden. Queda el sufijo del tipo.
        raiz = re.sub(r"-\d{4}-\d{2}-\d{2}(-\d+)?$", "", p)
        raiz = re.sub(r"-\d+$", "", raiz)
        if raiz in SUFIJOS:
            return SUFIJOS[raiz]

    cabeza = texto[:20000]
    # OJO: la marca tiene que estar SOLA en su linea. Un recorrido lleva sus
    # medidas de origen dentro, comentadas ("; [CIRCULOS]"), y buscar el texto
    # suelto lo hacia pasar por lamina: al guardar se ofrecia sobrescribir la
    # lamina de verdad con un G-code. Comentado es metadato; sin comentar es
    # el archivo mismo.
    if re.search(r"^[ 	]*\[CIRCULOS\][ 	]*$", cabeza, re.M):
        return "lamina"
    # El disenador guarda el dibujo como JSON con unos comentarios delante.
    if '"partName"' in cabeza or ('"entities"' in cabeza and '"points"' in cabeza):
        return "contorno"
    if re.search(r"^\s*;\s*Recorrido:", cabeza, re.M):
        return "recorrido-soldadura"

    hay_gcode = re.search(r"^\s*[GgMm]\d", cabeza, re.M)
    if hay_gcode:
        # Un recorrido de soldadura para el laser y aguanta; un corte se mueve
        # con el laser encendido. Las esperas G04 son la firma del punteado.
        esperas = len(re.findall(r"\bG0*4\b", cabeza))
        arcos = len(re.findall(r"\bG0*[23]\b", cabeza))
        if esperas >= 2 and arcos == 0:
            return "recorrido-soldadura"
        return "corte"

    if re.search(r"^\s*[^#;\n]*[-\d.]+\s*[,;\t ]\s*[-\d.]+\s*$", cabeza, re.M):
        return "coordenadas"
    return "desconocido"


def linea_identidad(tipo, proyecto, origen=None):
    """La linea que hace que un archivo diga lo que es."""
    hoy = datetime.date.today().isoformat()
    partes = ["GCODER v1", "tipo=" + (tipo or "desconocido")]
    if proyecto:
        partes.append("proyecto=" + re.sub(r"\s+", "_", proyecto))
    if origen:
        partes.append("origen=" + re.sub(r"\s+", "_", origen))
    partes.append("fecha=" + hoy)
    return " ".join(partes)


def poner_identidad(texto, tipo, proyecto, origen=None):
    # De donde salio el archivo es un dato que no se debe perder al volver a
    # guardarlo: si no, tras la primera edicion nadie sabe ya su procedencia.
    previa = cabecera_taller(texto) or {}
    if not origen:
        origen = previa.get("origen")
    """Antepone la linea de identidad, o actualiza la que ya hubiera.

    El comentario se elige segun el archivo: '#' para las laminas (su lector
    ya salta esas lineas) y ';' para el G-code, que es lo que entiende una
    maquina. Los dos se reconocen al leer.
    """
    # El G-code lleva ';' porque es lo que entiende una maquina; lo demas
    # (lamina, dibujo, listas) lleva '#', que es su comentario de siempre.
    marca = ";" if tipo in ("recorrido-soldadura", "corte", "recalibrado") else "#"
    nueva = marca + " " + linea_identidad(tipo, proyecto, origen)
    lineas = texto.split("\n")
    for i, l in enumerate(lineas[:8]):
        if re.match(r"^\s*[;#]\s*(?:GCODER|GFORGE|TALLER)\b", l):
            lineas[i] = nueva
            return "\n".join(lineas)
    return nueva + "\n" + texto


def _leer_texto(ruta):
    try:
        with io.open(ruta, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def ficha_archivo(carpeta, nombre):
    ruta = os.path.join(carpeta, nombre)
    try:
        st = os.stat(ruta)
    except OSError:
        return None
    texto = _leer_texto(ruta)
    tipo = detectar_tipo(texto, nombre)
    cab = cabecera_taller(texto) or {}
    return {
        "nombre": nombre,
        "tipo": tipo,
        "etiqueta": ETIQUETAS.get(tipo, tipo),
        "bytes": st.st_size,
        "modificado": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "origen": cab.get("origen") or "",
        "identificado": bool(cab),
    }


def ficha_proyecto(base, nombre):
    carpeta = os.path.join(carpeta_proyectos(base), nombre)
    if not os.path.isdir(carpeta):
        return None
    meta = {}
    ruta_meta = os.path.join(carpeta, "proyecto.json")
    if os.path.isfile(ruta_meta):
        try:
            with io.open(ruta_meta, encoding="utf-8") as fh:
                meta = json.load(fh)
        except Exception:
            meta = {}

    archivos = []
    for f in sorted(os.listdir(carpeta)):
        if f == "proyecto.json" or os.path.isdir(os.path.join(carpeta, f)):
            continue
        ficha = ficha_archivo(carpeta, f)
        if ficha:
            archivos.append(ficha)

    resumen = {}
    for a in archivos:
        resumen[a["tipo"]] = resumen.get(a["tipo"], 0) + 1

    try:
        tocado = max([os.stat(carpeta).st_mtime] +
                     [os.stat(os.path.join(carpeta, a["nombre"])).st_mtime for a in archivos])
    except (OSError, ValueError):
        tocado = 0

    return {
        "nombre": nombre,
        "notas": meta.get("notas", ""),
        "creado": meta.get("creado", ""),
        "archivos": archivos,
        "resumen": resumen,
        "modificado": datetime.datetime.fromtimestamp(tocado).isoformat(timespec="seconds") if tocado else "",
        "carpeta": carpeta,
    }


def listar_proyectos(base):
    raiz = carpeta_proyectos(base)
    if not os.path.isdir(raiz):
        return []
    fichas = []
    for n in sorted(os.listdir(raiz)):
        if not os.path.isdir(os.path.join(raiz, n)):
            continue
        if n.startswith("_"):      # la papelera no es un proyecto
            continue
        f = ficha_proyecto(base, n)
        if f:
            fichas.append(f)
    fichas.sort(key=lambda f: f["modificado"], reverse=True)
    return fichas


def crear_proyecto(base, nombre):
    nombre = nombre_seguro(nombre)
    if not nombre:
        raise ValueError("Nombre de proyecto no valido")
    if nombre.startswith("_"):
        raise ValueError("Un proyecto no puede empezar por '_'")
    raiz = carpeta_proyectos(base)
    carpeta = os.path.join(raiz, nombre)
    if os.path.isdir(carpeta):
        raise ValueError("Ya existe un proyecto llamado '%s'" % nombre)
    os.makedirs(carpeta)
    with io.open(os.path.join(carpeta, "proyecto.json"), "w", encoding="utf-8") as fh:
        json.dump({"nombre": nombre,
                   "creado": datetime.date.today().isoformat(),
                   "notas": ""}, fh, ensure_ascii=False, indent=2)
    return ficha_proyecto(base, nombre)


# tipo -> sufijo corto, el inverso de SUFIJOS.
SUFIJO_DE = dict((v, k) for k, v in SUFIJOS.items())

# Tipos que se rehacen en cada corrida: lo que los distingue es CUANDO se
# midieron, asi que su etiqueta es la fecha aunque lleven nombre dentro.
CON_FECHA = {"lamina"}
POR_FECHA_SIEMPRE = {"lamina"}

# La linea que Origen deja dentro de una lamina cuando le ha movido el cero.
# Una lamina recalibrada y la medicion de la que salio son del mismo tipo y
# del mismo dia: sin esto quedaban dos archivos que solo se distinguian por un
# "-2" al final.
RE_RECALIBRADO = re.compile(r"^\s*#\s*Recalibrado con Origen\b", re.M)

# Las carpetas que empiezan por '_' son cosas nuestras (la papelera), no
# proyectos. Ni se listan ni se dejan crear.
PAPELERA = "_papelera"


def nombre_interno(texto, tipo):
    """Como llamaste tu a esto dentro del programa.

    Cada tipo lo escribe en su cabecera, asi que no hace falta que los
    programas manden nada aparte: se lee del archivo.
    """
    cabeza = texto[:20000]
    if tipo == "recorrido-soldadura":
        m = re.search(r"^\s*;\s*Recorrido:\s*(.+?)\s*(?:\(|$)", cabeza, re.M)
    elif tipo == "lamina":
        m = re.search(r"^\s*#\s*L[\u00e1a]mina:\s*(.+)$", cabeza, re.M)
    elif tipo == "contorno":
        m = re.search(r'"partName"\s*:\s*"([^"]*)"', cabeza)
    else:
        m = None
    return (m.group(1).strip() if m else "")


def _etiqueta(nombre, pieza):
    """El nombre interno, dejado en algo que valga como nombre de archivo.

    Se quita la palabra del tipo cuando el nombre es el que pone el programa
    por defecto ("Recorrido 1" -> "1"): repetirla daria
    `Cervical.recorrido-Recorrido 1.txt`.
    """
    n = re.sub(r"^(recorrido|l[\u00e1a]mina|contorno|corte)\s+", "", nombre or "",
               flags=re.I).strip()
    n = re.sub(r"[\\/:*?\"<>|]", "", n)
    n = re.sub(r"\s+", " ", n).strip(" .-")
    # Si lo que queda es el nombre de la pieza, sobra: la pieza ya va delante.
    # "Lamina Cervical" dentro del proyecto Cervical no aporta nada.
    if _clave(n) == _clave(pieza):
        return ""
    return n


def _clave(nombre):
    """El nombre reducido a lo comparable: sin extension, ni puntos, ni mayusculas.

    Hace falta porque los programas pasan el nombre por su propio limpiador
    antes de descargar, y ahi se pierden los puntos: `Cervical.corte.txt`
    llega como `Cervicalcorte.txt` y aun asi es el mismo archivo.
    """
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(nombre or "")[0].lower())


def sugerir_nombre(base, proyecto, contenido, nombre_original="", abierto=""):
    """Como deberia llamarse esto dentro del proyecto.

    La convencion es `Pieza.tipo.txt`, que es lo que hace legible la carpeta:
    el nombre dice que es cada archivo sin abrirlo.

    Si viene de EDITAR un archivo del proyecto, lo que se espera es guardarlo
    encima, no dejar una copia numerada al lado: proponer otra cosa llenaria la
    carpeta de versiones y volveria a la duda de cual es la buena. Se propone
    sobrescribir, y se avisa de que lo hace.
    """
    tipo = detectar_tipo(contenido, nombre_original)
    pieza = nombre_seguro(proyecto) or "archivo"
    carpeta = os.path.join(carpeta_proyectos(base), pieza)

    abierto = nombre_seguro(abierto, con_punto=True)
    if abierto:
        ruta = os.path.join(carpeta, abierto)
        # Que coincida el TIPO no basta. Origen exporta recorridos nuevos a
        # partir de los puntos, y son del mismo tipo que el archivo del que
        # salieron: ofrecer sobrescribirlo destruiria el original. Quien sabe
        # de verdad lo que esta escribiendo es el programa, y lo dice en el
        # nombre que le pone; si ese nombre es otro, es otro archivo.
        mismo = _clave(nombre_original) == _clave(abierto)
        if (mismo and os.path.isfile(ruta)
                and detectar_tipo(_leer_texto(ruta), abierto) == tipo):
            return {"tipo": tipo, "etiqueta": ETIQUETAS.get(tipo, tipo),
                    "nombre": abierto, "sobrescribe": True}

    sufijo = SUFIJO_DE.get(tipo, "archivo")

    # Una LAMINA se vuelve a medir en cada corrida, asi que lo que distingue
    # una de otra es el dia, no un numero de orden: `Cervical.lamina-3.txt` no
    # dice nada y `Cervical.lamina-2026-09-03.txt` dice cual es. Los demas
    # tipos describen la pieza, no la corrida, y se siguen numerando; un
    # recorrido tampoco lleva fecha porque suele haber varios del mismo dia y
    # el numero es justo lo que los separa.
    # Lo que distingue a este archivo de otro del mismo tipo. Por orden:
    # el nombre que le pusiste tu; si no, la fecha para lo que se remide en
    # cada corrida; si no, un numero.
    etiqueta = "" if tipo in POR_FECHA_SIEMPRE else _etiqueta(
        nombre_interno(contenido, tipo), pieza)
    if not etiqueta and tipo in CON_FECHA:
        etiqueta = datetime.date.today().isoformat()
        # Una lamina a la que Origen le movio el cero ya no es la medicion:
        # es la medicion corregida. Sin decirlo en el nombre quedaban dos
        # archivos del mismo dia sin forma de saber cual era cual.
        if RE_RECALIBRADO.search(contenido[:20000]):
            etiqueta += "-recalibrado"

    if etiqueta:
        candidato = "%s.%s-%s.txt" % (pieza, sufijo, etiqueta)
        n = 2
        while os.path.exists(os.path.join(carpeta, candidato)):
            candidato = "%s.%s-%s-%d.txt" % (pieza, sufijo, etiqueta, n)
            n += 1
    else:
        candidato = "%s.%s.txt" % (pieza, sufijo)
        n = 2
        while os.path.exists(os.path.join(carpeta, candidato)):
            candidato = "%s.%s-%d.txt" % (pieza, sufijo, n)
            n += 1
    return {"tipo": tipo, "etiqueta": ETIQUETAS.get(tipo, tipo),
            "nombre": candidato, "sobrescribe": False}


def ruta_en_proyecto(base, proyecto, archivo):
    """La ruta real de un archivo dentro de un proyecto, o nada si se sale."""
    proyecto = nombre_seguro(proyecto)
    archivo = nombre_seguro(archivo, con_punto=True)
    if not proyecto or not archivo:
        return None
    raiz = os.path.realpath(carpeta_proyectos(base))
    destino = os.path.realpath(os.path.join(raiz, proyecto, archivo))
    try:
        if os.path.commonpath([destino, raiz]) != raiz:
            return None
    except ValueError:
        return None
    return destino


def renombrar_proyecto(base, viejo, nuevo):
    """Cambia el nombre de un proyecto entero, con todo lo que eso arrastra.

    El nombre del proyecto no vive solo en la carpeta: es la PIEZA del nombre
    de cada archivo (`Cervical.recorrido-Equis.txt`) y va en la linea de
    identidad de dentro. Mover solo la carpeta dejaria diez archivos diciendo
    que son de otra pieza, que es exactamente la confusion de la que salio
    toda esta forma de nombrar. Asi que se hacen las tres cosas.
    """
    viejo = nombre_seguro(viejo)
    nuevo = nombre_seguro(nuevo)
    if not viejo or not nuevo:
        raise ValueError("Nombre de proyecto no valido")
    if nuevo.startswith("_"):
        raise ValueError("Un proyecto no puede empezar por '_'")

    raiz = carpeta_proyectos(base)
    origen = os.path.join(raiz, viejo)
    destino = os.path.join(raiz, nuevo)
    if not os.path.isdir(origen):
        raise ValueError("El proyecto '%s' no existe" % viejo)
    if os.path.normcase(origen) == os.path.normcase(destino):
        return ficha_proyecto(base, viejo)
    if os.path.exists(destino):
        raise ValueError("Ya hay un proyecto llamado '%s'" % nuevo)

    os.rename(origen, destino)

    # La ficha del proyecto.
    ruta_meta = os.path.join(destino, "proyecto.json")
    if os.path.isfile(ruta_meta):
        try:
            with io.open(ruta_meta, encoding="utf-8") as fh:
                meta = json.load(fh)
            meta["nombre"] = nuevo
            with io.open(ruta_meta, "w", encoding="utf-8") as fh:
                json.dump(meta, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    renombrados, resellados = 0, 0
    for f in sorted(os.listdir(destino)):
        ruta = os.path.join(destino, f)
        if f == "proyecto.json" or not os.path.isfile(ruta):
            continue

        # La identidad de dentro dice de que proyecto es. Se corrige sin tocar
        # nada mas del archivo.
        texto = _leer_texto(ruta)
        if texto:
            cab = cabecera_taller(texto)
            if cab and cab.get("proyecto") == viejo:
                nuevo_texto = poner_identidad(
                    texto, cab.get("tipo") or detectar_tipo(texto, f), nuevo,
                    cab.get("origen"))
                if nuevo_texto != texto:
                    with io.open(ruta, "w", encoding="utf-8", newline="") as fh:
                        fh.write(nuevo_texto)
                    resellados += 1

        # El prefijo del nombre. Solo si de verdad era el del proyecto: un
        # archivo que se llame de otra forma se deja como esta.
        if f.startswith(viejo + "."):
            candidato = nuevo + f[len(viejo):]
            objetivo = os.path.join(destino, candidato)
            if not os.path.exists(objetivo):
                os.rename(ruta, objetivo)
                renombrados += 1

    ficha = ficha_proyecto(base, nuevo)
    ficha["renombrados"] = renombrados
    ficha["resellados"] = resellados
    return ficha


def tirar_proyecto(base, nombre):
    """Aparta un proyecto: lo mueve a la papelera, no lo borra.

    Un clic de mas no puede llevarse por delante un mes de mediciones. Queda
    en `Proyectos/_papelera/` con la fecha en el nombre, fuera de la lista
    pero a un paso en el Explorador. Vaciar la papelera es cosa tuya.
    """
    nombre = nombre_seguro(nombre)
    if not nombre:
        raise ValueError("Nombre de proyecto no valido")
    # La propia papelera no es un proyecto y no se puede meter dentro de si
    # misma: sin esto salia un error de Windows en crudo.
    if nombre.startswith("_"):
        raise ValueError("'%s' no es un proyecto" % nombre)
    raiz = carpeta_proyectos(base)
    origen = os.path.join(raiz, nombre)
    if not os.path.isdir(origen):
        raise ValueError("El proyecto '%s' no existe" % nombre)

    cuantos = len([f for f in os.listdir(origen)
                   if f != "proyecto.json" and os.path.isfile(os.path.join(origen, f))])

    papelera = os.path.join(raiz, PAPELERA)
    if not os.path.isdir(papelera):
        os.makedirs(papelera)

    sello = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
    destino = os.path.join(papelera, "%s (borrado %s)" % (nombre, sello))
    n = 2
    while os.path.exists(destino):
        destino = os.path.join(papelera, "%s (borrado %s) %d" % (nombre, sello, n))
        n += 1
    os.rename(origen, destino)
    return {"nombre": nombre, "archivos": cuantos, "papelera": os.path.normpath(destino)}


def renombrar_en_proyecto(base, proyecto, archivo, nuevo):
    """Cambia el nombre de un archivo dentro de su proyecto."""
    origen = ruta_en_proyecto(base, proyecto, archivo)
    if not nuevo.lower().endswith(".txt"):
        nuevo = nuevo + ".txt"
    destino = ruta_en_proyecto(base, proyecto, nuevo)
    if not origen or not destino:
        raise ValueError("Nombre no valido")
    if not os.path.isfile(origen):
        raise ValueError("No existe '%s'" % archivo)
    if os.path.normcase(origen) == os.path.normcase(destino):
        return {"nombre": os.path.basename(destino)}
    if os.path.exists(destino):
        raise ValueError("Ya hay un archivo llamado '%s'" % os.path.basename(destino))
    os.rename(origen, destino)
    return {"nombre": os.path.basename(destino)}


def abrir_en_explorador(base, proyecto, archivo=None):
    """Abre el Explorador de Windows en la carpeta del proyecto.

    Si se da un archivo, ademas lo deja seleccionado. Solo se abre lo que ya
    esta dentro de Proyectos: la ruta pasa por la misma comprobacion que todo
    lo demas, asi que de aqui no se puede lanzar nada de fuera.
    """
    carpeta = os.path.join(carpeta_proyectos(base), nombre_seguro(proyecto) or "")
    if not os.path.isdir(carpeta):
        raise ValueError("El proyecto '%s' no existe" % proyecto)

    destino = ruta_en_proyecto(base, proyecto, archivo) if archivo else None
    if destino and os.path.isfile(destino):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(destino)])
    else:
        subprocess.Popen(["explorer", os.path.normpath(carpeta)])
    return {"abierto": os.path.normpath(destino or carpeta)}


def guardar_en_proyecto(base, proyecto, archivo, contenido, tipo=None, origen=None):
    ruta = ruta_en_proyecto(base, proyecto, archivo)
    if not ruta:
        raise ValueError("Ruta no valida")
    if not os.path.isdir(os.path.dirname(ruta)):
        raise ValueError("El proyecto '%s' no existe" % proyecto)
    if not tipo:
        tipo = detectar_tipo(contenido, archivo)
    contenido = poner_identidad(contenido, tipo, proyecto, origen)
    with io.open(ruta, "w", encoding="utf-8", newline="") as fh:
        fh.write(contenido)
    return {"guardado": True, "ruta": ruta, "tipo": tipo,
            "ficha": ficha_archivo(os.path.dirname(ruta), os.path.basename(ruta))}


class Manejador(BaseHTTPRequestHandler):
    raiz = ""          # carpeta donde vive hub.html
    ruta_json = ""     # ruta a programas.json
    # Donde vive Proyectos/. Se pasa aparte a proposito: dentro del .exe los
    # recursos pueden salir de una carpeta temporal que se borra al cerrar, y
    # los proyectos del taller no pueden acabar ahi.
    base = ""

    def log_message(self, *args):
        pass  # sin ruido en consola

    def do_GET(self):
        ruta = unquote(urlparse(self.path).path)
        if ruta in ("", "/"):
            ruta = "/hub.html"

        if ruta == "/programas.json":
            return self._enviar_manifiesto()

        if ruta == "/api/proyectos":
            return self._json({"proyectos": listar_proyectos(self._base())})

        if ruta == "/api/archivo":
            q = parse_qs(urlparse(self.path).query)
            proy = (q.get("proyecto") or [""])[0]
            arch = (q.get("nombre") or [""])[0]
            destino = ruta_en_proyecto(self._base(), unquote(proy), unquote(arch))
            if not destino or not os.path.isfile(destino):
                return self._error(404, "No existe ese archivo en el proyecto")
            texto = _leer_texto(destino)
            return self._json({"nombre": os.path.basename(destino), "contenido": texto,
                               "tipo": detectar_tipo(texto, destino)})

        if ruta.startswith("/p/"):
            partes = ruta[3:].split("/", 1)
            pid = partes[0]
            resto = partes[1] if len(partes) > 1 else ""
            carpeta = self._carpeta_de(pid)
            if not carpeta:
                return self._error(404, "Programa desconocido: " + pid)
            return self._enviar_archivo(carpeta, resto)

        return self._enviar_archivo(self.raiz, ruta.lstrip("/"))

    def do_POST(self):
        ruta = unquote(urlparse(self.path).path)
        try:
            largo = int(self.headers.get("Content-Length") or 0)
            cuerpo = json.loads(self.rfile.read(largo).decode("utf-8")) if largo else {}
        except Exception as exc:
            return self._error(400, "Cuerpo invalido: %s" % exc)

        try:
            if ruta == "/api/proyectos":
                return self._json({"proyecto": crear_proyecto(self._base(), cuerpo.get("nombre"))})

            if ruta == "/api/sugerir":
                return self._json(sugerir_nombre(
                    self._base(), cuerpo.get("proyecto"),
                    cuerpo.get("contenido") or "", cuerpo.get("nombre") or "",
                    cuerpo.get("abierto") or ""))

            if ruta == "/api/proyecto/renombrar":
                return self._json(renombrar_proyecto(
                    self._base(), cuerpo.get("nombre"),
                    (cuerpo.get("nuevo") or "").strip()))

            if ruta == "/api/proyecto/borrar":
                return self._json(tirar_proyecto(self._base(), cuerpo.get("nombre")))

            if ruta == "/api/renombrar":
                return self._json(renombrar_en_proyecto(
                    self._base(), cuerpo.get("proyecto"), cuerpo.get("nombre"),
                    (cuerpo.get("nuevo") or "").strip()))

            if ruta == "/api/explorar":
                return self._json(abrir_en_explorador(
                    self._base(), cuerpo.get("proyecto"), cuerpo.get("nombre")))

            if ruta == "/api/archivo":
                res = guardar_en_proyecto(
                    self._base(), cuerpo.get("proyecto"), cuerpo.get("nombre"),
                    cuerpo.get("contenido") or "", cuerpo.get("tipo"), cuerpo.get("origen"))
                return self._json(res)
        except ValueError as exc:
            return self._error(400, str(exc))
        except OSError as exc:
            return self._error(500, str(exc))

        return self._error(404, "Ruta desconocida: " + ruta)

    # ---- utilidades internas ----

    def _base(self):
        """La carpeta que manda: donde se crea y se busca Proyectos/."""
        if self.base and os.path.isdir(self.base):
            return self.base
        return os.path.dirname(os.path.abspath(self.ruta_json))

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _carpeta_de(self, pid):
        try:
            datos = leer_manifiesto(self.ruta_json)
        except Exception:
            return None
        for prog in datos.get("programas", []):
            if prog.get("id") == pid:
                carpeta = prog.get("carpeta") or ""
                return carpeta if os.path.isdir(carpeta) else None
        return None

    def _enviar_manifiesto(self):
        try:
            cuerpo = json.dumps(leer_manifiesto(self.ruta_json), ensure_ascii=False).encode("utf-8")
        except Exception as exc:
            return self._error(500, "programas.json invalido: %s" % exc)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _enviar_archivo(self, base, relativo):
        base_real = os.path.realpath(base)
        destino = os.path.realpath(os.path.join(base_real, relativo.replace("/", os.sep)))

        # No dejar escapar de la carpeta montada (p.ej. /p/soldadura/../../algo)
        try:
            if os.path.commonpath([destino, base_real]) != base_real:
                return self._error(403, "Ruta fuera de la carpeta del programa")
        except ValueError:
            return self._error(403, "Ruta invalida")

        if not os.path.isfile(destino):
            return self._error(404, "No encontrado: " + relativo)

        tipo = mimetypes.guess_type(destino)[0] or "application/octet-stream"
        if tipo.startswith("text/") or tipo in ("application/javascript", "application/json"):
            tipo += "; charset=utf-8"
        try:
            with open(destino, "rb") as fh:
                cuerpo = fh.read()
        except OSError as exc:
            return self._error(500, str(exc))

        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")  # siempre la version recien guardada
        self.end_headers()
        self.wfile.write(cuerpo)

    def _error(self, codigo, mensaje):
        cuerpo = mensaje.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)


def iniciar(raiz, ruta_json, puerto=0, base=None):
    """Arranca el servidor en un hilo. Devuelve (servidor, puerto)."""
    Manejador.raiz = raiz
    Manejador.ruta_json = ruta_json
    Manejador.base = base or os.path.dirname(os.path.abspath(ruta_json))
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    servidor.daemon_threads = True
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    return servidor, servidor.server_address[1]
