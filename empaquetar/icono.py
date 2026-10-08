# -*- coding: utf-8 -*-
"""
Genera el icono de GCoder: icono.ico (para el .exe) y logotipo.png (para el hub).

    python icono.py

La idea del dibujo es la que define todo el conjunto: **encontrar el centro de
un punto**. Una placa oscura, la retícula de la máquina, el punto del láser
encendido y la cruz de centrado encima. Es lo que hace el Localizador de
Centro, y es de donde salio el nombre de Origen.

Se dibuja a 4x y se reduce con LANCZOS: es la forma barata de tener bordes
suaves sin depender de un motor de antialiasing.

Hay DOS dibujos a propósito. A 16 px una cruz fina desaparece y queda una
mancha: el icono de la barra de tareas dejaría de reconocerse. Así que los
tamaños pequeños llevan una versión con menos elementos y trazos más gruesos
—misma idea, menos detalle—, que es como se resuelve esto de siempre.
"""

import os

from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))

# Los mismos colores del hub, para que el icono y la ventana sean lo mismo.
FONDO_ALTO = (38, 43, 40)      # grafito cálido
FONDO_BAJO = (24, 27, 25)
REJILLA    = (58, 66, 61)
LASER      = (217, 84, 31)     # --laser
LASER_VIVO = (247, 147, 61)
MARFIL     = (240, 236, 227)

ESCALA = 4


def _lienzo(lado):
    """Placa con degradado y esquinas redondeadas."""
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))

    grad = Image.new("RGBA", (1, lado))
    for y in range(lado):
        t = y / max(1, lado - 1)
        grad.putpixel((0, y), tuple(
            int(a + (b - a) * t) for a, b in zip(FONDO_ALTO, FONDO_BAJO)) + (255,))
    grad = grad.resize((lado, lado))

    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [0, 0, lado - 1, lado - 1], radius=int(lado * 0.22), fill=255)
    img.paste(grad, (0, 0), mascara)
    return img, mascara


def _resplandor(lado, cx, cy, radio, color):
    """El halo del láser. Un disco desenfocado: barato y convincente."""
    capa = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse(
        [cx - radio, cy - radio, cx + radio, cy + radio], fill=color + (150,))
    return capa.filter(ImageFilter.GaussianBlur(radio * 0.42))


def _capa(lado):
    """Una capa suelta para dibujar y luego COMPONER.

    Dibujar directo sobre la imagen con un color semitransparente no la mezcla:
    ImageDraw REEMPLAZA el pixel, alfa incluido, y donde deberia haber una
    linea tenue queda un agujero por el que se ve lo que hay detras de la
    ventana. Por eso cada cosa translucida se pinta aparte y se compone.
    """
    return Image.new("RGBA", (lado, lado), (0, 0, 0, 0))


# Cual de las propuestas es el icono de la app. Se ven todas con:
#     python icono_variantes.py
ELEGIDO = "G"


def dibujar(lado, detallado=True):
    """El icono de la app: el dibujo ELEGIDO, y nada mas.

    La importacion va aqui dentro a proposito: icono_variantes usa las piezas
    de este modulo, asi que hacerla arriba seria morderse la cola.
    """
    from icono_variantes import POR_NOMBRE
    return POR_NOMBRE[ELEGIDO](lado, detallado)


def reticula(lado, detallado=True):
    """La cruz de centrado sobre el punto. Ahora es el icono de Origen."""
    img, mascara = _lienzo(lado)
    d = ImageDraw.Draw(img)
    c = lado / 2.0
    u = lado / 100.0          # una unidad = 1% del lado, para escalar todo

    if detallado:
        # Retícula de la mesa: casi no se ve, solo da fondo de taller.
        rej = _capa(lado)
        dr = ImageDraw.Draw(rej)
        paso = lado / 5.0
        for i in range(1, 5):
            p = i * paso
            dr.line([(p, 0), (p, lado)], fill=REJILLA + (58,), width=max(1, int(u * 0.9)))
            dr.line([(0, p), (lado, p)], fill=REJILLA + (58,), width=max(1, int(u * 0.9)))
        img.alpha_composite(rej)

        # El agujero de la pieza: cuatro arcos con hueco donde pasan los brazos.
        # Partido —y no un circulo entero— para que se lea como una marca de
        # medicion y no como la mira de un arma.
        aro = _capa(lado)
        da = ImageDraw.Draw(aro)
        r = u * 31
        for ini in (12, 102, 192, 282):
            da.arc([c - r, c - r, c + r, c + r], ini, ini + 66,
                   fill=MARFIL + (150,), width=int(u * 2.6))
        img.alpha_composite(aro)

        # Brazos de la cruz de centrado, con hueco en el medio para que el
        # punto respire y no se convierta en una mancha.
        brazos = _capa(lado)
        db = ImageDraw.Draw(brazos)
        largo, hueco, grosor = u * 43, u * 17, int(u * 3.2)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            db.line([(c + dx * hueco, c + dy * hueco),
                     (c + dx * largo, c + dy * largo)],
                    fill=MARFIL + (215,), width=grosor)
        img.alpha_composite(brazos)

        # El punto: lo que manda en el icono.
        img.alpha_composite(_resplandor(lado, c, c, u * 21, LASER))
        r = u * 12
        d.ellipse([c - r, c - r, c + r, c + r], fill=LASER + (255,))
        r = u * 5.5
        d.ellipse([c - r, c - r, c + r, c + r], fill=LASER_VIVO + (255,))
    else:
        # Versión de tamaño pequeño: sin rejilla ni anillo, trazos gruesos y
        # el punto más grande. A 16 px esto sigue leyéndose; lo otro no.
        largo, hueco, grosor = u * 45, u * 21, int(u * 7)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            d.line([(c + dx * hueco, c + dy * hueco),
                    (c + dx * largo, c + dy * largo)],
                   fill=MARFIL + (235,), width=grosor)
        img.alpha_composite(_resplandor(lado, c, c, u * 20, LASER))
        r = u * 15
        d.ellipse([c - r, c - r, c + r, c + r], fill=LASER + (255,))
        r = u * 6.5
        d.ellipse([c - r, c - r, c + r, c + r], fill=LASER_VIVO + (255,))

    # El resplandor se sale de las esquinas redondeadas; se recorta.
    recorte = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    recorte.paste(img, (0, 0), mascara)
    return recorte


def render(lado):
    detallado = lado >= 48
    grande = dibujar(lado * ESCALA, detallado)
    return grande.resize((lado, lado), Image.LANCZOS)


def main():
    tamanos = [256, 128, 64, 48, 32, 24, 16]
    capas = [render(t) for t in tamanos]

    ico = os.path.join(RAIZ, "icono.ico")
    capas[0].save(ico, format="ICO",
                  sizes=[(t, t) for t in tamanos],
                  append_images=capas[1:])

    png = os.path.join(RAIZ, "logotipo.png")
    render(256).save(png, format="PNG")

    # Tira de contacto, solo para revisar a simple vista como queda en cada
    # tamano sin tener que abrir el explorador.
    ancho = sum(t for t in tamanos) + 20 * len(tamanos)
    tira = Image.new("RGBA", (ancho, 300), (250, 250, 248, 255))
    x = 10
    for t, capa in zip(tamanos, capas):
        tira.paste(capa, (x, 20 + (256 - t) // 2), capa)
        x += t + 20
    tira.save(os.path.join(AQUI, "icono_muestra.png"))

    print("icono.ico    ->", ico, "(%d capas: %s)" % (len(tamanos), tamanos))
    print("logotipo.png ->", png)
    print("muestra     ->", os.path.join(AQUI, "icono_muestra.png"))


if __name__ == "__main__":
    main()
