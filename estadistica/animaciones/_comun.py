# _comun.py — utilidades compartidas de la capa de animación (Manim).
#
# La capa de animación del laboratorio de estadística corre en un entorno conda
# APARTE (manim-datafw) porque Manim trae dependencias pesadas (pango, cairo,
# ffmpeg) que no deben contaminar el runtime del lab interactivo (matplotlib).
# Por eso este módulo NO importa simuladores/config.py (que depende de
# matplotlib, ausente en el env de Manim): reproduce solo las CONSTANTES de
# paleta (no lógica) para mantener la identidad visual. El guion bajo lo excluye
# de cualquier descubrimiento de escenas.
#
# Prohibido copiar estas utilidades en cada escena: importarlas desde aquí.

from manim import *
import numpy as np

# --- Paleta del laboratorio (misma que simuladores/config.py; solo constantes) ---
AZUL = "#2E5496"       # primera serie / curva principal
AZUL_OSC = "#1F3864"   # títulos, anotaciones
ROJO = "#9E2A2B"       # segunda serie / shocks
DORADO = "#C9A227"     # curva teórica / equilibrio
GRIS = "#B0B7C3"       # ejes, líneas auxiliares
VERDE = "#3A7D44"      # tercera serie / población


def rng(semilla):
    """Generador reproducible (convención del lab: aleatoriedad con semilla fija,
    como m17). Toda escena que simule debe fijar su semilla."""
    return np.random.default_rng(semilla)


def titulo_lab(texto):
    """Título con la identidad tipográfica del laboratorio (serif, azul)."""
    return Text(texto, color=AZUL_OSC, weight=BOLD).scale(0.8).to_edge(UP, buff=0.35)


def histograma(datos, ejes, bins, rango, color, opacidad=0.85):
    """VGroup de barras de un histograma (densidad) en coordenadas de `ejes`.
    Reutilizable por cualquier escena que muestre distribuciones simuladas."""
    conteo, bordes = np.histogram(datos, bins=bins, range=rango, density=True)
    barras = VGroup()
    for i in range(len(conteo)):
        alto = float(conteo[i])
        if alto <= 0:
            continue
        x0, x1 = float(bordes[i]), float(bordes[i + 1])
        ll, ur = ejes.c2p(x0, 0), ejes.c2p(x1, alto)
        barra = Rectangle(width=ur[0] - ll[0], height=ur[1] - ll[1],
                          fill_color=color, fill_opacity=opacidad,
                          stroke_width=0.4, stroke_color=WHITE)
        barra.move_to(ejes.c2p((x0 + x1) / 2, alto / 2))
        barras.add(barra)
    return barras


def pdf_normal(mu, sd):
    """Densidad normal N(mu, sd^2) como función graficable con ejes.plot."""
    return lambda x: np.exp(-((x - mu) ** 2) / (2 * sd ** 2)) / (sd * np.sqrt(2 * np.pi))
