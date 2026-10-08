# Guion de videos — GCoder

Borrador para revisar juntos antes de grabar. Cada video es un MP4 independiente,
numerado en el orden en que se montan.

---

## 1. Cómo se graban

| Parámetro | Valor |
|---|---|
| Resolución | 1920 × 1080, 30 fps, MP4 (H.264), sin audio |
| Qué se graba | GCoder en Chromium, servido con `servir.py`. Es la misma interfaz que `GCoder.exe`. |
| Cursor | Visible, con un pulso al hacer clic. Las medidas se teclean a velocidad humana. |
| Ritmo | Pausa breve tras cada acción para que se lea el resultado. 1 s quieto al empezar y 1.5 s al terminar, como margen para las transiciones del montaje. |
| Datos | Se graba sobre una **copia** de la carpeta. Tu `Proyectos/` real no se toca. |
| Nombres | `NN_Programa_Tema.mp4` (por ejemplo `03_Disenador_ContornoExterior.mp4`) |

**Diferencias con el `.exe` que no se pueden evitar:**

- Los diálogos nativos de Windows (elegir archivo, "Guardar fuera…") no aparecen en la grabación. Cuando se carga un archivo, un rótulo dice cuál se eligió.
- En los guardados dentro de un proyecto no pasa nada de esto: el diálogo es el de GCoder y sí se ve.

---

## 2. La historia que cuentan los videos

Dos piezas nuevas, creadas desde cero, recorren todos los programas.

### Pieza A — `Placa` (contorno para CORTE)

Placa de 40 × 24 mm con el cero en la esquina inferior izquierda.

- **Contorno exterior:** 4 líneas y una esquina redondeada R6, con el centro del arco en (34, 18).
- **4 agujeros Ø3:** en (5, 5), (35, 5), (5, 19) y (34, 18). El último es concéntrico con la esquina, así que sirve para la restricción "Concéntrico".
- **Hexágono** de apotema 3 centrado en (20, 7).
- **Ventana rectangular** de 14 × 5, de (13, 15) a (27, 20).
- **Agujero Ø2** dibujado con Círculo de 3 puntos en (28, 7).

### Pieza B — `Lamina` (contorno para PUNTOS DE SOLDADURA)

Lámina de 12 × 10 mm de Nitinol, con esquinas R2.

- **6 huecos Ø1.75** en (3, 3), (6, 3), (9, 3), (3, 7), (6, 7) y (9, 7).
- En los huecos van los puntos de soldadura.
- Las lecturas "de máquina" que se teclean en Soldadura son esos centros más un desplazamiento de unos 12 mm en X y 5 mm en Y, con un error de ±0.01 mm. Así parecen medidas reales y tiene sentido alinear el contorno.

### Recorrido de cada pieza

```
                ┌──────────────► Editor de G-code (orden, revisión, simulación)
 Diseñador ─────┤  Placa.corte.txt
 de Contornos   │
                └─ Lamina.corte.txt ─► Soldadura Láser ("G-code / contorno de referencia")
                                          │  medir huecos → puntos → materiales → recorridos
                                          ├─► Lamina.lamina-AAAA-MM-DD.txt
                                          └─► Lamina.recorrido-1.txt ─► Editor de G-code
                                                                     └─► Origen (calibrador: recuperar el cero)
```

> **Supuesto que confirmar:**
> - "Geometría de referencia" es el panel **"G-code (contorno de referencia)"** de Soldadura Láser.
> - "Calibrador" es **Origen**, que recalibra el cero de pieza.

---

## 3. Lista de videos

Las duraciones son aproximadas: unos **60 min** en total, en 33 videos.

| # | Programa | Tema | ≈ min |
|---|---|---|---|
| 00 | Hub | Bienvenida: pestañas, colores, chip de proyecto, Recargar | 1 |
| 01 | Proyectos | Crear los proyectos `Placa` y `Lamina` | 1 |
| 02 | Diseñador | La pantalla y la vista | 1.5 |
| 03 | Diseñador | Contorno exterior con Línea y Arco (medidas exactas) | 2.5 |
| 04 | Diseñador | Agujeros: Círculo C+R, Círculo 3 puntos, Polígono, Rectángulo | 2.5 |
| 05 | Diseñador | Seleccionar, editar propiedades, arrastrar, eliminar, deshacer | 2 |
| 06 | Diseñador | Restricciones (las 10) | 3 |
| 07 | Diseñador | Cotas, capa Construcción y visibilidad de capas | 2 |
| 08 | Diseñador | Orden de corte, materiales y G-code → guardar en el proyecto | 3 |
| 09 | Diseñador | Contorno de la lámina para soldadura y su G-code | 2.5 |
| 10 | Editor | Abrir el corte desde el proyecto y leer el programa | 1.5 |
| 11 | Editor | Orden de corte: arrastrar, Revisión, Encajar, plegar | 2.5 |
| 12 | Editor | Evitar lo cortado (nido de 3 piezas) | 1.5 |
| 13 | Editor | Sentido de corte, desactivar piezas, variables | 2.5 |
| 14 | Editor | Prueba en vivo (simulación) | 1.5 |
| 15 | Editor | Editar el texto a mano, guardar, archivos que no le tocan | 2 |
| 16 | Soldadura | La pantalla y el contorno de referencia | 1.5 |
| 17 | Soldadura | Medir un hueco con N puntos | 2 |
| 18 | Soldadura | Medir con 6 puntos (cascada) y con Directo | 2.5 |
| 19 | Soldadura | Revisar puntos: construcción, editar, renombrar, borrar | 2 |
| 20 | Soldadura | Alinear el contorno con lo medido | 1.5 |
| 21 | Soldadura | Materiales y variables | 1 |
| 22 | Soldadura | Recorridos de soldadura | 3 |
| 23 | Soldadura | Exportar: recorrido, punto suelto, variables, ZIP | 2 |
| 24 | Soldadura | Guardar la lámina, limpiar y volver a cargar; avisos | 2 |
| 25 | Editor | Revisar un recorrido de soldadura | 1.5 |
| 26 | Origen | Abrir y comprobar posiciones | 1.5 |
| 27 | Origen | Recuperar el cero perdido (el caso principal) | 2.5 |
| 28 | Origen | Otras correcciones: nuevo 0,0, mover solo uno, N puntos, incremental | 2.5 |
| 29 | Origen | Recalibrar una lámina | 1.5 |
| 30 | Origen | Recorridos en Origen | 2.5 |
| 31 | Origen | Origen con un programa de corte | 1.5 |
| 32 | Proyectos | Lo que quedó en el proyecto: abrir, renombrar, quitar | 2 |

---

## 4. Guion detallado

Formato de cada video: **Parte de** (estado inicial), pasos con **Acción** y **Rótulo**, y **Termina con**.

- **Acción**: lo que se ve en pantalla.
- **Rótulo**: el texto corto que explica el paso. Puede ir como subtítulo `.srt` o incrustado.

### 00 · Bienvenida: el hub GCoder

**Parte de:** GCoder recién abierto, en la pantalla Proyectos (solo está la Cervical de ejemplo).

| # | Acción | Rótulo |
|---|---|---|
| 1 | Plano general quieto | GCoder reúne los programas del taller en una sola ventana. |
| 2 | Pasar el cursor por las pestañas | Una pestaña por programa: Soldadura, Diseñador, Editor y Origen. |
| 3 | Clic en Soldadura, Diseñador, Editor y Origen (hilo de color arriba) | Cada programa tiene su color: naranja, azul, violeta y verde. |
| 4 | Señalar "Cortes de Stent · PENDIENTE" | Lo que todavía no existe aparece en gris como pendiente. |
| 5 | Señalar el nombre del archivo `…_v1.xx.html` arriba a la derecha | Aquí se ve qué versión del programa está cargada. |
| 6 | Señalar el chip "sin proyecto" y "Recargar" | El chip dice qué proyecto está abierto; Recargar busca versiones nuevas sin cerrar. |
| 7 | Volver a Proyectos | Todo empieza eligiendo la pieza. |

**Termina con:** la pantalla Proyectos.

### 01 · Proyectos: crear las piezas de la demo

**Parte de:** la pantalla Proyectos.

| # | Acción | Rótulo |
|---|---|---|
| 1 | Señalar la tarjeta Cervical: pastillas de colores y lista de archivos | Cada proyecto es una pieza; dentro está todo lo suyo. |
| 2 | Señalar los colores de tipo: lámina, recorrido, corte, contorno | El color dice qué es cada archivo sin abrirlo. |
| 3 | Escribir "Placa" en Nuevo proyecto → Crear | Nuevo proyecto: se crea su carpeta y queda abierto. |
| 4 | Aparece el toast y el chip pasa a "Placa" | Todo lo que se guarde ahora irá a la carpeta de Placa. |
| 5 | Crear "Lamina" de la misma forma | La segunda pieza: la lámina que se va a soldar. |
| 6 | Clic en la tarjeta Placa → botón "Diseñador de Contornos" | Se abre el programa con el proyecto ya puesto. |

**Termina con:** el Diseñador vacío y el chip en "Placa".

### 02 · Diseñador · La pantalla y la vista

**Parte de:** el Diseñador vacío, con el proyecto Placa.

| # | Acción | Rótulo |
|---|---|---|
| 1 | Recorrer las tres columnas con el cursor | Herramientas a la izquierda, dibujo en el centro, propiedades y G-code a la derecha. |
| 2 | Escribir en Nombre de la pieza "Placa" y en Nombre de archivo "Placa" | El nombre de la pieza va en la cabecera del G-code. |
| 3 | Señalar Láser / Construcción | Lo que se dibuja en Láser se corta; Construcción solo sirve de guía. |
| 4 | Pasar el cursor por el lienzo (coordenadas en vivo) | Abajo se leen las coordenadas en milímetros. El 0,0 es el cero de pieza. |
| 5 | Rueda para acercar y alejar; arrastrar en vacío; botones + − ⤢ | Rueda para el zoom, arrastrar para moverse, ⤢ para encuadrar. |
| 6 | Señalar los atajos (tooltips de herramientas) | Cada herramienta tiene su tecla: L línea, R rectángulo, C círculo… |

### 03 · Diseñador · Contorno exterior con Línea y Arco

| # | Acción | Rótulo |
|---|---|---|
| 1 | Tecla L, clic en (0, 0) | Línea: primer clic en el cero de pieza. |
| 2 | Escribir Distancia 40, Ángulo 0, clic | Se escribe la medida exacta y el clic la confirma. |
| 3 | Aparece el glifo H (Horizontal automática) | Si sigue una guía, la restricción se pone sola. |
| 4 | Distancia 18, ángulo 90, clic → V | La línea sigue encadenada desde el punto anterior. |
| 5 | Esc. Tecla A: centro (34, 18), inicio (40, 18), fin (34, 24) | Arco: centro, inicio y fin. Esquina redondeada R6. |
| 6 | L desde (34, 24) hasta (0, 24) y luego al (0, 0); se engancha al punto inicial | El último clic se engancha al primer punto y el contorno queda cerrado. |
| 7 | Esc Esc. ⤢ | Contorno exterior terminado. |

### 04 · Diseñador · Agujeros

| # | Acción | Rótulo |
|---|---|---|
| 1 | C → clic en (5, 5) → modo Diámetro, valor 3 → Colocar círculo | Círculo centro + radio: se puede dar el diámetro exacto. |
| 2 | Clic en (35, 5), (5, 19) y (34, 18) | El diámetro se recuerda: cada clic es otro agujero igual. |
| 3 | El último agujero se engancha al centro del arco (◎) | El cursor se engancha a centros, puntos medios y extremos. |
| 4 | T (Círculo 3 puntos): (27, 7), (29, 7), (28, 8) | Círculo por 3 puntos: útil para copiar un agujero medido. |
| 5 | P (Polígono): clic en (20, 7), 6 lados, apotema 3; se ve el resumen | Polígono regular: por radio, apotema, lado o diámetro. |
| 6 | Colocar polígono | Hexágono colocado. |
| 7 | R (Rectángulo): clic en (13, 15), Ancho 14, Alto 5, Enter | Rectángulo con ancho y alto exactos. |

### 05 · Diseñador · Seleccionar, editar, arrastrar, eliminar

| # | Acción | Rótulo |
|---|---|---|
| 1 | S, clic en un borde de la ventana → panel Propiedades | Seleccionar muestra las medidas de la figura. |
| 2 | Cambiar el alto a 6 → Enter | Las medidas se editan desde las propiedades. |
| 3 | Clic en un agujero → Diámetro 3.2 → Enter | |
| 4 | Arrastrar una esquina de la ventana | Los puntos se pueden arrastrar. |
| 5 | Ctrl+Z ×3, Ctrl+Y ×1 | Ctrl+Z deshace y Ctrl+Y rehace. Hasta 60 pasos. |
| 6 | E (Eliminar): clic en una línea suelta de prueba | Eliminar quita la figura entera y lo que dependa de ella. |
| 7 | Seleccionar algo → Supr; Esc limpia la selección | |

### 06 · Diseñador · Restricciones

| # | Acción | Rótulo |
|---|---|---|
| 1 | Señalar "Relaciones automáticas al dibujar" y la lista actual | Las restricciones mantienen la geometría cuando se mueve algo. |
| 2 | Seleccionar dos agujeros (Ctrl+clic) → = Iguales | Iguales: los dos tienen el mismo diámetro. |
| 3 | Agujero (34, 18) + arco de esquina → ◎ Concéntricos | Concéntricos: comparten el centro. |
| 4 | Lado superior y lado derecho de la ventana → ⊥ Perpendiculares | |
| 5 | Lados inferior y superior de la ventana → ∥ Paralelas | |
| 6 | Línea de construcción + círculo → T Tangente (en una figura de prueba) | |
| 7 | Punto + línea → · Punto en línea | |
| 8 | Esquina (0, 0) → ▣ Fijar punto. Arrastrar otra esquina: la fijada no se mueve | Fijar: ese punto ya no se mueve nunca. |
| 9 | Dos puntos sueltos → ⊕ Unir puntos | |
| 10 | Señalar "N restricciones · M grados de libertad" y borrar una con ✕ | La lista dice cuántas hay y cuántos grados de libertad quedan. |

### 07 · Diseñador · Cotas, construcción y capas

| # | Acción | Rótulo |
|---|---|---|
| 1 | D: clic en (0, 0) y en (40, 0) → aparece 40.00 | Cota de distancia entre dos puntos. |
| 2 | Cota radio sobre el arco de la esquina → R6.00 | Cota de radio sobre un círculo o arco. |
| 3 | Seleccionar la cota y cambiar a 42 → la placa se alarga; Ctrl+Z | Al editar una cota se mueve la geometría. |
| 4 | Construcción → línea de eje de (0, 12) a (40, 12) en gris → volver a Láser | Lo de Construcción sirve de guía y no se corta. |
| 5 | Capas: ocultar y mostrar Cotas, Traslado y Construcción | Las capas solo cambian lo que se ve. |

### 08 · Diseñador · Orden de corte, materiales y G-code

| # | Acción | Rótulo |
|---|---|---|
| 1 | "Trazo de traslado (N tramos)": señalar los números y flechas verdes en el dibujo | El orden en que se cortan las figuras. |
| 2 | ↑ ↓ para cambiar el orden → ↻ Actualizar | El contorno exterior siempre se corta el último. |
| 3 | G-code de corte: G54, Absoluto, F corte 150, F traslado 600 | Parámetros del programa de corte. |
| 4 | + Material "Acero 0.5" → + variable ×2 → editar las F de cada variable → elegir material y V2 | Un material guarda varias combinaciones de velocidad. |
| 5 | ⤢ Expandir y recorrer el G-code: M08 / M07 / G02 / G03 / M09 | M07 enciende el láser, M09 lo apaga. Exterior horario, agujeros antihorario. |
| 6 | Alternar Incremental y volver a Absoluto | |
| 7 | 💾 Exportar → modal "Guardar en «Placa»" → `Placa.corte.txt` → Guardar | Guardar en el proyecto: el nombre lo propone GCoder. |
| 8 | 💾 Guardar .txt → `Placa.contorno.txt` → Guardar | El dibujo se guarda aparte para poder volver a editarlo. |
| 9 | Limpiar todo → Ctrl+Z | Limpiar todo también se puede deshacer. |

### 09 · Diseñador · Contorno de la lámina para soldadura

**Parte de:** Proyectos → tarjeta Lamina → Diseñador. Ritmo más ágil, porque las herramientas ya se vieron.

| # | Acción | Rótulo |
|---|---|---|
| 1 | Pieza "Lamina", archivo "Lamina" | La segunda pieza: una lámina de 12 × 10 mm. |
| 2 | 4 líneas + 4 arcos R2 con medidas exactas | Contorno con esquinas redondeadas. |
| 3 | 6 círculos Ø1.75 en los huecos | En estos huecos irán los puntos de soldadura. |
| 4 | Seleccionar los 6 → Iguales | |
| 5 | Ver "7 trayectorias · 6 interiores · 1 exterior" | |
| 6 | Absoluto, G54 → 💾 Exportar → `Lamina.corte.txt` | Este G-code servirá de referencia en Soldadura Láser. |
| 7 | Guardar .txt → `Lamina.contorno.txt` | |

### 10 · Editor · Abrir el corte y leer el programa

| # | Acción | Rótulo |
|---|---|---|
| 1 | Proyectos → tarjeta Placa → Editor de G-code (se abre `Placa.corte.txt`) | Desde el proyecto, cada programa abre el archivo que le toca. |
| 2 | Recorrer Programa: líneas, piezas, G54, ocupa X/Y, recorrido cortando y en vacío, tiempo | El Editor lee el programa como lo haría la máquina. |
| 3 | Lista Orden de corte y números en el dibujo | Cada figura es una pieza con su número de orden. |
| 4 | Clic en una fila: se resalta en el dibujo; otro clic la suelta | |
| 5 | Capas: Cortes, Traslados, Números, Sentido | |
| 6 | Revisión en verde: "Orden correcto" | Revisión: lo de dentro se corta antes que lo que lo rodea. |

### 11 · Editor · Orden de corte

| # | Acción | Rótulo |
|---|---|---|
| 1 | Arrastrar el contorno exterior al puesto 1 | Error a propósito: cortar el exterior primero. |
| 2 | Avisos en rojo y traslados en rojo | La pieza se soltaría antes de cortar sus agujeros. |
| 3 | Ctrl+Z | |
| 4 | ⤵ Encajar por geometría: los agujeros quedan dentro de la boca del exterior | Encajar mete cada figura dentro de la que la rodea. |
| 5 | Arrastrar un agujero dentro de la boca; ▲ ▼ | Dentro de la boca se reordena libremente. |
| 6 | ⊟ Plegar todo / ⊞ Desplegar todo | |
| 7 | ↺ Orden del archivo | Vuelve al orden original del archivo. |

### 12 · Editor · Evitar lo cortado

**Parte de:** se abre `Nido_3_cervicales.txt`, el ejemplo incluido con 3 piezas en una sola lámina.

| # | Acción | Rótulo |
|---|---|---|
| 1 | Datos: 27 piezas, 2 min 6 s, avisos de traslado en rojo | Un traslado pasa por encima de una pieza ya suelta. |
| 2 | ⤵ Encajar por geometría | Primero se encaja… |
| 3 | ↝ Evitar lo cortado → 0 avisos, el tiempo baja | …y después se busca un orden que no pase por encima de lo cortado. |

### 13 · Editor · Sentido de corte, desactivar piezas y variables

| # | Acción | Rótulo |
|---|---|---|
| 1 | ⇄ sobre un agujero → aviso de sentido → botón "⇄ Invertir" del aviso | Agujeros antihorario, exterior horario. |
| 2 | Quitar el interruptor del hexágono: gris, `;OFF` en el G-code | Desactivar no borra: queda comentado en el archivo. |
| 3 | Volver a activarlo | |
| 4 | Coordenadas 55, F de corte 180 (Tab) | Cambia todas las líneas que usan ese valor. |
| 5 | Incrementales G91 → ver el texto → Absolutas | Convierte el programa entre absolutas e incrementales. |
| 6 | Aceleración 500 → cambia el tiempo estimado | La aceleración solo afina el tiempo estimado. |

### 14 · Editor · Prueba en vivo

| # | Acción | Rótulo |
|---|---|---|
| 1 | ×5 → ▶ Probar | La simulación corta el programa en el orden real. |
| 2 | Espacio (pausa) → Espacio (sigue) | Cabezal naranja cortando, verde en vacío. |
| 3 | Esc (rebobina) → ×20 → hasta el final | "Recorrido terminado". |

### 15 · Editor · Texto a mano, guardar y archivos que no le tocan

| # | Acción | Rótulo |
|---|---|---|
| 1 | Escribir `; revisado` antes de M30 → nota roja → ✓ Aplicar texto | También se puede editar el G-code a mano. |
| 2 | Otro cambio → ↺ Descartar | |
| 3 | 💾 Guardar .txt → modal → `Placa.corte.txt` (encima) → Guardar | Al guardar se propone el mismo archivo que se abrió. |
| 4 | Abrir `Lamina.contorno.txt` → mensaje rojo | Si se abre un archivo que no le toca, avisa a dónde va. |

### 16 · Soldadura · La pantalla y el contorno de referencia

| # | Acción | Rótulo |
|---|---|---|
| 1 | Proyectos → Lamina → Soldadura Láser | Soldadura Láser localiza los centros de los huecos y genera el G-code. |
| 2 | Recorrer: método, resultado actual, puntos, materiales, recorridos | |
| 3 | Desplegar "G-code (contorno de referencia)" → Subir archivo → `Lamina.corte.txt` | El G-code de corte sirve de dibujo de referencia. |
| 4 | ⤢; Ocultar movimiento | En negro lo que corta y en azul los traslados. |

### 17 · Soldadura · Medir con N puntos

| # | Acción | Rótulo |
|---|---|---|
| 1 | Nombre "Punto 1"; teclear 3 bordes del hueco 1 (lecturas de máquina) | En la máquina se lleva la retícula a 3 puntos del borde del hueco. |
| 2 | Aparecen el círculo discontinuo y Centro X/Y, Radio, Diámetro, Área | Con 3 puntos ya se calcula el círculo. |
| 3 | Enter → el punto pasa a la lista | |
| 4 | Punto 2: + Agregar punto ×2 (5 bordes) → CALCULAR | Con más puntos se ajusta por mínimos cuadrados. |
| 5 | − Quitar último | |

### 18 · Soldadura · 6 puntos y Directo

| # | Acción | Rótulo |
|---|---|---|
| 1 | 6 puntos: Par A (dos bordes a la misma Y) | Método en cascada: cada par se apoya en el anterior. |
| 2 | Los campos en gris se rellenan solos | Las coordenadas que ya se saben se rellenan solas. |
| 3 | Par B y Par C → Cx1, Cx2 y ΔX | Par C confirma la X. ΔX en rojo avisaría de una mala medida. |
| 4 | Promedio → CALCULAR (Punto 3) | |
| 5 | Medir los huecos 4 y 5 con 6 puntos (ritmo rápido) | |
| 6 | Directo: Cx, Cy y Diámetro 1.75 → CALCULAR (Punto 6) | Directo: cuando el centro ya se conoce. |

### 19 · Soldadura · Revisar los puntos

| # | Acción | Rótulo |
|---|---|---|
| 1 | Mostrar construcción: mediatrices, residuos | Se ve cómo se calculó cada centro. |
| 2 | Clic en la fila del Punto 2 → corregir un borde → ACTUALIZAR PUNTO | |
| 3 | ‹ › para navegar; Cancelar edición | |
| 4 | Renombrar en la lista; agregar un punto de prueba y borrarlo con × | |

### 20 · Soldadura · Alinear el contorno con lo medido

| # | Acción | Rótulo |
|---|---|---|
| 1 | El contorno (coordenadas de pieza) y los puntos (coordenadas de máquina) no coinciden | El dibujo está en coordenadas de pieza y las medidas en las de la máquina. |
| 2 | Arrastrar el contorno hasta que los huecos caigan sobre los puntos | Se arrastra el contorno hasta que encaja. |
| 3 | Ajustar Offset X/Y a mano | |
| 4 | Reiniciar posición → volver a ponerlo | |

### 21 · Soldadura · Materiales y variables

| # | Acción | Rótulo |
|---|---|---|
| 1 | + Nuevo material → "Nitinol" | Cada material guarda sus tiempos de soldadura. |
| 2 | + Variable: "Capas 1,2" = 18; "Capas 2,3" = 8 | Cada variable es un G04 P según las capas que se unen. |

### 22 · Soldadura · Recorridos

| # | Acción | Rótulo |
|---|---|---|
| 1 | + Nuevo recorrido → clic en los puntos 1, 2, 3, 6, 5 y 4 en el lienzo → Listo | El recorrido es el orden en que se sueldan los puntos. |
| 2 | Flechas y números en el dibujo | |
| 3 | Absoluto / Incremental; Asent. 100, Suelda 18, Sist. coord. G58 | Parámetros propios de cada recorrido. |
| 4 | Material Nitinol → píldora "Capas 1,2 · P18" | El material pone el tiempo de soldadura. |
| 5 | ⛭ Vista previa: G04, M08, M07, M09 | Ir al punto, esperar, gas, láser, soldar, apagar. |
| 6 | ↑ ↓ para reordenar y × para quitar un paso | |
| 7 | Segundo recorrido "Cruzado" (1, 6, 3, 4, 2, 5), otro color | Varios recorridos para repartir el calor. |
| 8 | 👁 y "Ocultar en lienzo" | |

### 23 · Soldadura · Exportar

| # | Acción | Rótulo |
|---|---|---|
| 1 | ⬇ Exportar .txt del Recorrido 1 → modal → `Lamina.recorrido-1.txt` → Guardar | El recorrido se guarda en el proyecto, con sus medidas dentro. |
| 2 | Exportar el 2.º recorrido | |
| 3 | ⬇ de un solo paso → programa de un punto | Para probar un solo punto. |
| 4 | Píldora "Todos" → un archivo por variable | |
| 5 | Exportar todos los puntos (individual) → ZIP | Un programa por punto, todos en un ZIP. |

### 24 · Soldadura · Guardar la lámina, limpiar y recargar

| # | Acción | Rótulo |
|---|---|---|
| 1 | 💾 Guardar .txt → `Lamina.lamina-AAAA-MM-DD.txt` | La lámina lleva la fecha porque se vuelve a medir en cada corrida. |
| 2 | Limpiar todo | Se van los puntos y los recorridos; quedan los materiales y el contorno. |
| 3 | 📂 Cargar .txt → la lámina guardada | Al cargar se recupera todo. |
| 4 | Cargar `Lamina.recorrido-1.txt` | Un recorrido lleva dentro las medidas de las que salió. |
| 5 | Cargar `Lamina.corte.txt` → aviso rojo | Un programa de corte no va aquí: va al Editor. |

### 25 · Editor · Revisar un recorrido de soldadura

| # | Acción | Rótulo |
|---|---|---|
| 1 | Proyectos → Lamina → Editor → `Lamina.recorrido-1.txt` | El Editor también lee recorridos de soldadura. |
| 2 | "Orden de soldadura", "Puntos de soldadura", G04 soldar y asentar | |
| 3 | Arrastrar un punto: el camino en vacío cambia | El orden decide el camino en vacío. |
| 4 | ×1 Probar: el cabezal se detiene en cada punto ("esperando") | |

### 26 · Origen · Abrir y comprobar

| # | Acción | Rótulo |
|---|---|---|
| 1 | Proyectos → Lamina → Origen → `Lamina.recorrido-1.txt` | Origen recupera el cero de pieza cuando se pierde. |
| 2 | Panel Archivo: elementos, G58, ocupa X/Y | |
| 3 | Comprobación: clic en las luces (correcta / incorrecta) | Se marca qué posiciones se comprobaron en la máquina. |
| 4 | Quitar la soldadura de un punto: "sin soldar" y `;OFF` | |

### 27 · Origen · Recuperar el cero perdido

| # | Acción | Rótulo |
|---|---|---|
| 1 | Situación: se movió la lámina y el cero ya no vale | La lámina se movió y el programa ya no cae sobre los huecos. |
| 2 | Seleccionar el Punto 1 (lista o dibujo) | Se elige un hueco del dibujo como referencia. |
| 3 | 6 puntos: teclear las lecturas nuevas (cascada) → Centro medido | Se mide ese hueco en la máquina. |
| 4 | "Es donde está el elegido" → Nueva X/Y | |
| 5 | ⌖ Mover el cero aquí → ⤢ → "Cero movido" | Todo el programa se desplaza para caer donde se midió. |
| 6 | G-code: solo cambian las coordenadas | |
| 7 | 💾 Guardar .txt → modal → nombre sugerido → Guardar | |

### 28 · Origen · Otras correcciones

| # | Acción | Rótulo |
|---|---|---|
| 1 | Seleccionar Punto 4 → Partir de donde está → corregir Y → → Mover solo este | Mover solo este: corrige un punto sin tocar los demás. |
| 2 | Ctrl+Z / Ctrl+Y | |
| 3 | N puntos (3 bordes, + borde) → "Es el nuevo 0,0" | El hueco medido pasa a ser el 0,0. |
| 4 | Abrir `Prueba_5puntos_inc.txt` (incremental) → mover el cero (1 línea) → mover A3 (2 líneas) | En incrementales solo se recalculan los saltos necesarios. |

### 29 · Origen · Recalibrar una lámina

| # | Acción | Rótulo |
|---|---|---|
| 1 | Proyectos → Lamina → Origen → la lámina medida | |
| 2 | Medir y mover el cero aquí | |
| 3 | Salida "La lámina recalibrada": `# Recalibrado con Origen` y `;OFFSET` | La lámina corregida guarda también el contorno desplazado. |
| 4 | Guardar → `Lamina.lamina-AAAA-MM-DD-recalibrado.txt` | El nombre deja claro que es la medición corregida. |

### 30 · Origen · Recorridos

| # | Acción | Rótulo |
|---|---|---|
| 1 | Parámetros → Recorrido nuevo: aparece "Recorrido 1" con todos los puntos | Origen también monta recorridos. |
| 2 | + Nuevo recorrido → + Añadir puntos → clics → volver a pulsar uno lo quita → ✓ Listo | |
| 3 | ▲ ▼ ✕; renombrar "Lado derecho" | |
| 4 | Cero G56, G91 inc, F 600, G04 25/150 | Cada recorrido tiene sus propios parámetros. |
| 5 | ▸ G-code; clic en la otra tarjeta | El seleccionado es el que sale abajo. |
| 6 | ⬇ Exportar → archivo nuevo en el proyecto | Un recorrido exportado es siempre un archivo nuevo. |

### 31 · Origen · Con un programa de corte

| # | Acción | Rótulo |
|---|---|---|
| 1 | Abrir `Placa.corte.txt` → trayectorias y "F de corte" | |
| 2 | Seleccionar un agujero → Mover el cero aquí | En un corte, la referencia es el punto donde empieza a cortar. |
| 3 | Coordenadas → 55 | |

### 32 · Proyectos · Lo que quedó en el proyecto

| # | Acción | Rótulo |
|---|---|---|
| 1 | Tarjetas Placa y Lamina con sus archivos de colores | Cada pieza tiene ya todos sus archivos. |
| 2 | Pasar el cursor por los nombres (de dónde viene cada uno) | |
| 3 | Botón de un programa en la fila de un archivo → se abre ahí | Cada archivo se puede abrir en cualquier programa que lo lea. |
| 4 | ✎ Renombrar un archivo | |
| 5 | ✎ Renombrar el proyecto: los archivos de dentro cambian también | |
| 6 | ✕ Quitar un proyecto de prueba → va a `_papelera` | Quitar no borra: lo manda a la papelera. |

---

## 5. Lo que queda fuera, y por qué

- **Cortes de Stent:** está marcado como pendiente; solo aparece en el video 00.
- **Funciones exclusivas de Windows o de `GCoder.exe`:**
  - diálogo nativo de guardar;
  - ↗ "Abrir en el Explorador";
  - `GCoder.exe --info`;
  - `ABRIR GCoder.bat`.

  No se pueden grabar aquí. Si las quieres, son 10–20 s que puedes grabar tú en tu equipo.
- **Diseñador → Variable "Todas (un archivo por variable)":** está roto (ver abajo).

## 6. Fallos encontrados al analizar

No los arreglo sin que me lo digas. En los videos simplemente se evitan.

1. **Diseñador:** exportar con la variable "Todas (un archivo por variable)" da un error (`downloadBlob` no existe) y no descarga nada.
2. **Diseñador dentro de un proyecto** (riesgo de perder el dibujo):
   - Al abrir `Pieza.contorno.txt`, el nombre de archivo pasa a "Pieza.contorno".
   - Si después se pulsa Exportar G-code, GCoder propone guardar el G-code ENCIMA del contorno.
3. **Soldadura → Exportar todos:** al quitar la píldora, el campo Suelda sigue mostrando el valor de la variable, aunque se exporta con otro.
4. **Editor:** los puntos de un recorrido salen como "Punto Punto 1".
5. **Origen:** al recalibrar un recorrido, las MEDIDAS DE ORIGEN que lleva comentadas dentro no se actualizan.
