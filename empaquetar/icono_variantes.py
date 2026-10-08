# -*- coding: utf-8 -*-
"""
Propuestas para el icono de la app. Genera empaquetar/icono_propuestas.png.

    python icono_variantes.py

La elegida se copia a icono.py como dibujo definitivo.

Todas se juzgan en la columna de 16 px, no en la de 160: en la barra de tareas
y en la pestaña del Explorador es donde el icono tiene que hacer su trabajo, y
es donde se cae casi cualquier dibujo con detalle.

El perfil del yunque se define UNA vez, en coordenadas 0..100, y de ahi sale
todo: la escala, donde cae su cara de golpear y donde tiene que aterrizar el
haz. Asi no hay numeros sueltos que ajustar a ojo cada vez que se mueve algo.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

from icono import (AQUI, ESCALA, LASER, LASER_VIVO, MARFIL, _capa, _lienzo,
                   _resplandor, reticula)

ACERO = (166, 173, 168)
ACERO_ALTO = (208, 213, 208)
ACERO_BAJO = (101, 109, 103)

# Perfil clasico, de izquierda a derecha: el cuerno, la cara de golpear, el
# talon, la cintura y la base.
YUNQUE = [
    (2, 40),                                # punta del cuerno
    (21, 29), (32, 26),                     # lomo del cuerno hasta la cara
    (96, 26), (96, 43), (74, 43),           # cara de golpear y el talon
    (67, 60), (90, 60), (90, 78),           # cintura y base, por la derecha
    (10, 78), (10, 60), (33, 60),           # base y cintura, por la izquierda
    (26, 43), (6, 46),                      # bajo la cara y vuelta al cuerno
]
CARA_Y = 26.0          # altura de la cara de golpear, en el perfil
CARA_X = 58.0          # donde conviene que caiga el haz: sobre la cara, no en el cuerno

# El perfil ya ocupa casi todo el ancho (x de 2 a 96), asi que la escala baja
# de 1: si no, el dibujo se sale del marco y deja de leerse como un yunque.
ESC = 0.80
ESC_MINI = 0.90


def _centro(perfil):
    xs = [p[0] for p in perfil]
    ys = [p[1] for p in perfil]
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0


CX0, CY0 = _centro(YUNQUE)


def _map(lado, escala, x, y, dy=0.0):
    """Del perfil a la pantalla, centrando la figura en el marco."""
    u = lado / 100.0
    c = lado / 2.0
    return (c + (x - CX0) * escala * u,
            c + (y - CY0) * escala * u + dy * u)


def _yunque(lado, escala, dy=0.0, relleno=True, grosor=3.4):
    capa = _capa(lado)
    d = ImageDraw.Draw(capa)
    u = lado / 100.0
    pts = [_map(lado, escala, x, y, dy) for x, y in YUNQUE]
    if relleno:
        d.polygon(pts, fill=ACERO + (255,))
        # Filo claro arriba y sombra en la base: volumen sin degradados.
        d.line([pts[2], pts[3]], fill=ACERO_ALTO + (255,), width=max(1, int(u * 2.2 * escala)))
        d.line([pts[9], pts[10]], fill=ACERO_BAJO + (255,), width=max(1, int(u * 2.0 * escala)))
    else:
        d.line(pts + [pts[0]], fill=ACERO_ALTO + (255,),
               width=max(1, int(u * grosor * escala)), joint="curve")
    return capa


def _haz(lado, cx, cy, ancho_alto, ancho_bajo, alto=6.0, brillo=1.0):
    u = lado / 100.0
    capa = _capa(lado)
    ImageDraw.Draw(capa).polygon(
        [(cx - u * ancho_alto, u * alto), (cx + u * ancho_alto, u * alto),
         (cx + u * ancho_bajo, cy), (cx - u * ancho_bajo, cy)],
        fill=LASER_VIVO + (int(108 * brillo),))
    capa = capa.filter(ImageFilter.GaussianBlur(u * 1.7))

    nucleo = _capa(lado)
    ImageDraw.Draw(nucleo).polygon(
        [(cx - u * ancho_alto * .32, u * alto), (cx + u * ancho_alto * .32, u * alto),
         (cx + u * ancho_bajo * .45, cy), (cx - u * ancho_bajo * .45, cy)],
        fill=MARFIL + (int(212 * brillo),))
    capa.alpha_composite(nucleo.filter(ImageFilter.GaussianBlur(u * .8)))
    return capa


def _chispas(lado, cx, cy, n=8, largo=16.0):
    u = lado / 100.0
    capa = _capa(lado)
    d = ImageDraw.Draw(capa)
    for i in range(n):
        a = math.pi + (i + .5) * math.pi / n            # abanico hacia arriba
        L = u * largo * (.5 + .5 * ((i * 7) % 5) / 4.0)
        d.line([(cx, cy), (cx + math.cos(a) * L, cy + math.sin(a) * L * .8)],
               fill=LASER_VIVO + (185,), width=max(1, int(u * 1.1)))
    return capa.filter(ImageFilter.GaussianBlur(u * .5))


def _punto(img, lado, cx, cy, r_u, aplastado=.58):
    """El punto al rojo donde da el laser."""
    u = lado / 100.0
    img.alpha_composite(_resplandor(lado, cx, cy, u * r_u * 2.1, LASER))
    d = ImageDraw.Draw(img)
    r = u * r_u
    d.ellipse([cx - r, cy - r * aplastado, cx + r, cy + r * aplastado], fill=LASER + (255,))
    r *= .42
    d.ellipse([cx - r, cy - r * aplastado, cx + r, cy + r * aplastado], fill=LASER_VIVO + (255,))


def _cerrar(img, mascara):
    fuera = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fuera.paste(img, (0, 0), mascara)
    return fuera


# ================================================================ variantes
def yunque_haz(lado, detallado=True):
    """D - El yunque macizo y el haz cayendo sobre su cara."""
    img, mascara = _lienzo(lado)
    esc = ESC if detallado else ESC_MINI
    px, py = _map(lado, esc, CARA_X, CARA_Y, 4)

    img.alpha_composite(_haz(lado, px, py, 12 if detallado else 15, 3 if detallado else 4.5))
    img.alpha_composite(_yunque(lado, esc, dy=4))
    if detallado:
        img.alpha_composite(_chispas(lado, px, py))
    _punto(img, lado, px, py, 7 if detallado else 10)
    return _cerrar(img, mascara)


def contorno_haz(lado, detallado=True):
    """E - El yunque en contorno y el haz por delante. Lo que pediste."""
    img, mascara = _lienzo(lado)
    esc = ESC if detallado else ESC_MINI
    px, py = _map(lado, esc, CARA_X, CARA_Y, 4)

    img.alpha_composite(_yunque(lado, esc, dy=4, relleno=False,
                                grosor=3.4 if detallado else 5.6))
    img.alpha_composite(_haz(lado, px, py, 12 if detallado else 15,
                             3 if detallado else 4.5, brillo=1.15))
    _punto(img, lado, px, py, 7.5 if detallado else 10.5)
    return _cerrar(img, mascara)


def yunque_centrado(lado, detallado=True):
    """F - Como D pero el haz cae en el centro de la cara, mas simetrico."""
    img, mascara = _lienzo(lado)
    esc = ESC if detallado else ESC_MINI
    px, py = _map(lado, esc, 64, CARA_Y, 4)
    px = lado / 2.0                                    # justo en el eje del marco

    img.alpha_composite(_haz(lado, px, py, 13 if detallado else 16, 3.2 if detallado else 4.8))
    img.alpha_composite(_yunque(lado, esc, dy=4))
    if detallado:
        img.alpha_composite(_chispas(lado, px, py, n=9, largo=18))
    _punto(img, lado, px, py, 7.5 if detallado else 10.5)
    return _cerrar(img, mascara)


def haz_solo(lado, detallado=True):
    """G - El haz sobre la lamina, sin yunque."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    suelo = c + u * 18

    img.alpha_composite(_haz(lado, c, suelo, 17 if detallado else 20,
                             3.5 if detallado else 5, alto=8))

    lam = _capa(lado)
    dl = ImageDraw.Draw(lam)
    grosor = u * (8 if detallado else 11)
    dl.rounded_rectangle([u * 13, suelo, lado - u * 13, suelo + grosor],
                         radius=grosor / 2, fill=ACERO + (255,))
    if detallado:
        dl.line([(u * 17, suelo + grosor * .28), (lado - u * 17, suelo + grosor * .28)],
                fill=ACERO_ALTO + (150,), width=max(1, int(u * 1.4)))
    img.alpha_composite(lam)

    if detallado:
        img.alpha_composite(_chispas(lado, c, suelo, n=9, largo=17))
    _punto(img, lado, c, suelo, 9 if detallado else 12)
    return _cerrar(img, mascara)


# ====================================================== la familia del haz
def _haz_libre(lado, x0, y0, x1, y1, w0, w1, color, alfa, desenfoque):
    """Un haz entre dos puntos cualesquiera, no solo vertical.

    Se construye el cuadrilatero a partir de la NORMAL del eje, asi que vale
    igual para un haz recto que para uno inclinado y no hay que escribir dos
    versiones del mismo dibujo.
    """
    u = lado / 100.0
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L                      # perpendicular unitaria
    capa = _capa(lado)
    ImageDraw.Draw(capa).polygon(
        [(x0 + nx * u * w0, y0 + ny * u * w0), (x0 - nx * u * w0, y0 - ny * u * w0),
         (x1 - nx * u * w1, y1 - ny * u * w1), (x1 + nx * u * w1, y1 + ny * u * w1)],
        fill=color + (alfa,))
    return capa.filter(ImageFilter.GaussianBlur(u * desenfoque))


def _cono(lado, x0, y0, x1, y1, ancho, brillo=1.0):
    """Cono de luz con su nucleo, entre dos puntos."""
    capa = _haz_libre(lado, x0, y0, x1, y1, ancho, ancho * 0.22,
                      LASER_VIVO, int(108 * brillo), 1.7)
    capa.alpha_composite(_haz_libre(lado, x0, y0, x1, y1, ancho * .33, ancho * .09,
                                    MARFIL, int(212 * brillo), .8))
    return capa


def _lamina(lado, suelo, grosor, margen=13.0, hueco=0.0, contorno=False):
    """La lamina de abajo. Con `hueco` se parte en dos: el haz la ha cortado."""
    u = lado / 100.0
    capa = _capa(lado)
    d = ImageDraw.Draw(capa)
    r = grosor / 2.0
    tramos = [(u * margen, lado / 2.0 - u * hueco / 2.0),
              (lado / 2.0 + u * hueco / 2.0, lado - u * margen)] if hueco else \
             [(u * margen, lado - u * margen)]
    for x0, x1 in tramos:
        if contorno:
            d.rounded_rectangle([x0, suelo, x1, suelo + grosor], radius=r,
                                outline=ACERO_ALTO + (255,), width=max(1, int(u * 2.6)))
        else:
            d.rounded_rectangle([x0, suelo, x1, suelo + grosor], radius=r,
                                fill=ACERO + (255,))
    return capa


def haz_boquilla(lado, detallado=True):
    """H - El haz sale de la boquilla del cabezal."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    boca = u * (30 if detallado else 26)
    suelo = c + u * 22

    # el cabezal
    cab = _capa(lado)
    dc = ImageDraw.Draw(cab)
    ancho = 15 if detallado else 18
    dc.polygon([(c - u * ancho, u * 7), (c + u * ancho, u * 7),
                (c + u * ancho * .38, boca), (c - u * ancho * .38, boca)],
               fill=ACERO + (255,))
    dc.line([(c - u * ancho, u * 7), (c + u * ancho, u * 7)],
            fill=ACERO_ALTO + (255,), width=max(1, int(u * 3)))
    img.alpha_composite(cab)

    img.alpha_composite(_cono(lado, c, boca, c, suelo, 7 if detallado else 9))
    img.alpha_composite(_lamina(lado, suelo, u * (8 if detallado else 11),
                                margen=13 if detallado else 10))
    if detallado:
        img.alpha_composite(_chispas(lado, c, suelo, n=9, largo=16))
    _punto(img, lado, c, suelo, 8.5 if detallado else 11.5)
    return _cerrar(img, mascara)


def haz_cortando(lado, detallado=True):
    """I - El haz ya ha atravesado la lamina: se ve la ranura."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    suelo = c + u * 16
    grosor = u * (9 if detallado else 12)

    img.alpha_composite(_cono(lado, c, u * 8, c, suelo + grosor,
                              16 if detallado else 19, brillo=1.1))
    img.alpha_composite(_lamina(lado, suelo, grosor,
                                margen=12 if detallado else 9,
                                hueco=15 if detallado else 20))
    # El corte, encendido por dentro: es lo que hay que ver.
    img.alpha_composite(_resplandor(lado, c, suelo + grosor / 2, u * 13, LASER))
    if detallado:
        # chispas hacia abajo, que es por donde sale el material
        capa = _capa(lado)
        dd = ImageDraw.Draw(capa)
        for i in range(7):
            a = (i + .5) * math.pi / 7
            L = u * 14 * (.5 + .5 * ((i * 7) % 5) / 4.0)
            dd.line([(c, suelo + grosor), (c + math.cos(a) * L, suelo + grosor + math.sin(a) * L)],
                    fill=LASER_VIVO + (180,), width=max(1, int(u * 1.1)))
        img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(u * .5)))
    # El punto va en la CARA de arriba, no en medio del canto: si se centra,
    # tapa la ranura y el dibujo deja de contar que esta cortando.
    _punto(img, lado, c, suelo, 6 if detallado else 8.5)
    return _cerrar(img, mascara)


def haz_contorno(lado, detallado=True):
    """J - Todo en contorno, como el yunque que te gusto; solo el punto macizo."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    suelo = c + u * 20
    ancho = 11 if detallado else 13

    # Los dos cantos del cono, que ACABAN en el punto: si quedan abiertos
    # abajo, el dibujo se lee como unas tijeras y no como un haz.
    canto = _capa(lado)
    dk = ImageDraw.Draw(canto)
    for signo in (-1, 1):
        dk.line([(c + signo * u * ancho, u * 8), (c + signo * u * 1.4, suelo)],
                fill=MARFIL + (220,), width=max(1, int(u * (2.6 if detallado else 4.4))))
    img.alpha_composite(canto)
    img.alpha_composite(_cono(lado, c, u * 8, c, suelo, ancho * .8, brillo=.55))

    img.alpha_composite(_lamina(lado, suelo, u * (9 if detallado else 12),
                                margen=13 if detallado else 10, contorno=True))
    _punto(img, lado, c, suelo, 8.5 if detallado else 11.5)
    return _cerrar(img, mascara)


def haz_diagonal(lado, detallado=True):
    """K - El haz entra inclinado. Silueta mas viva."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    suelo = c + u * 20
    origen = (c - u * 30, u * 6)

    img.alpha_composite(_cono(lado, origen[0], origen[1], c, suelo,
                              14 if detallado else 17))
    img.alpha_composite(_lamina(lado, suelo, u * (8 if detallado else 11),
                                margen=12 if detallado else 9))
    if detallado:
        img.alpha_composite(_chispas(lado, c, suelo, n=8, largo=17))
    _punto(img, lado, c, suelo, 8.5 if detallado else 11.5)
    return _cerrar(img, mascara)


def haz_boquilla_charco(lado, detallado=True):
    """M - La boquilla de la H con el charco ancho de la L."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    boca = u * (28 if detallado else 24)
    suelo = c + u * 22

    cab = _capa(lado)
    dc = ImageDraw.Draw(cab)
    ancho = 15 if detallado else 18
    dc.polygon([(c - u * ancho, u * 6), (c + u * ancho, u * 6),
                (c + u * ancho * .36, boca), (c - u * ancho * .36, boca)],
               fill=ACERO + (255,))
    dc.line([(c - u * ancho, u * 6), (c + u * ancho, u * 6)],
            fill=ACERO_ALTO + (255,), width=max(1, int(u * 3)))
    img.alpha_composite(cab)

    img.alpha_composite(_cono(lado, c, boca, c, suelo, 6 if detallado else 8, brillo=1.2))
    img.alpha_composite(_lamina(lado, suelo, u * (8 if detallado else 11),
                                margen=11 if detallado else 8))
    if detallado:
        img.alpha_composite(_chispas(lado, c, suelo, n=10, largo=20))
    img.alpha_composite(_resplandor(lado, c, suelo, u * 24, LASER))
    d = ImageDraw.Draw(img)
    r = u * (13 if detallado else 15)
    d.ellipse([c - r, suelo - r * .34, c + r, suelo + r * .34], fill=LASER + (255,))
    r *= .38
    d.ellipse([c - r, suelo - r * .5, c + r, suelo + r * .5], fill=LASER_VIVO + (255,))
    return _cerrar(img, mascara)


def haz_estrecho(lado, detallado=True):
    """L - Haz fino y charco fundido ancho: mas potencia, menos foco."""
    img, mascara = _lienzo(lado)
    u = lado / 100.0
    c = lado / 2.0
    suelo = c + u * 18

    img.alpha_composite(_cono(lado, c, u * 6, c, suelo, 9 if detallado else 12, brillo=1.25))
    img.alpha_composite(_lamina(lado, suelo, u * (8 if detallado else 11),
                                margen=11 if detallado else 8))
    if detallado:
        img.alpha_composite(_chispas(lado, c, suelo, n=11, largo=24))
    # el charco: mas ancho y mas aplastado que un punto
    img.alpha_composite(_resplandor(lado, c, suelo, u * 26, LASER))
    d = ImageDraw.Draw(img)
    r = u * (14 if detallado else 16)
    d.ellipse([c - r, suelo - r * .34, c + r, suelo + r * .34], fill=LASER + (255,))
    r *= .38
    d.ellipse([c - r, suelo - r * .5, c + r, suelo + r * .5], fill=LASER_VIVO + (255,))
    return _cerrar(img, mascara)


# El registro que consulta icono.py para saber cual dibujar. Cambiar ELEGIDO
# alli y volver a generar es todo lo que hace falta para cambiar el icono.
POR_NOMBRE = {
    "D": yunque_haz,
    "E": contorno_haz,
    "F": yunque_centrado,
    "G": haz_solo,
    "H": haz_boquilla,
    "I": haz_cortando,
    "J": haz_contorno,
    "K": haz_diagonal,
    "L": haz_estrecho,
    "M": haz_boquilla_charco,
    "R": reticula,
}

# Agrupadas por idea, para poder comparar peras con peras.
FAMILIAS = {
    "haz": [
        ("G  Haz sobre lámina", haz_solo),
        ("H  Con boquilla", haz_boquilla),
        ("I  Cortando (con ranura)", haz_cortando),
        ("J  Todo en contorno", haz_contorno),
        ("K  Diagonal", haz_diagonal),
        ("L  Haz fino, charco ancho", haz_estrecho),
        ("M  Boquilla + charco", haz_boquilla_charco),
    ],
    "yunque": [
        ("D  Yunque + haz", yunque_haz),
        ("E  Contorno + haz", contorno_haz),
        ("F  Yunque, haz centrado", yunque_centrado),
        ("R  Retícula", reticula),
    ],
}


def render(fn, lado):
    return fn(lado * ESCALA, lado >= 48).resize((lado, lado), Image.LANCZOS)


def main(familia="haz"):
    variantes = FAMILIAS.get(familia) or FAMILIAS["haz"]
    tamanos = [160, 64, 48, 32, 16]
    fila = 200
    hoja = Image.new("RGBA", (600, fila * len(variantes) + 20), (250, 250, 248, 255))
    d = ImageDraw.Draw(hoja)
    for i, (nombre, fn) in enumerate(variantes):
        y = 20 + i * fila
        d.text((16, y + 74), nombre, fill=(60, 62, 58, 255))
        x = 150
        for t in tamanos:
            capa = render(fn, t)
            hoja.paste(capa, (x, y + (160 - t) // 2), capa)
            x += t + 22
    salida = os.path.join(AQUI, "icono_propuestas.png")
    hoja.save(salida)
    print("propuestas ->", salida)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "haz")
