# config.py — laboratorio de macroeconomía computacional (simuladores/).
#
# Todo lo ajustable vive aquí: rutas de salida, paleta, formato de figuras y
# tipografía académica. Las libs (base.py, reporte.py) no hardcodean nada de esto.

import os
from pathlib import Path

import matplotlib

# Plasma/Wayland: el plugin Qt "wayland" puede faltar; xcb (X11) es el
# fallback estable para los modos interactivos. Solo se toca si el usuario
# no lo definió ya.
if os.environ.get("WAYLAND_DISPLAY") and "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

DIR_BASE = Path(__file__).resolve().parent
DIR_MODELOS = DIR_BASE / "modelos"
DIR_SALIDAS = DIR_BASE / "salidas"   # reportes MD + figuras generadas (regenerable, no se versiona)

# Paleta sobria del laboratorio (la misma que usaba el IS-LM original)
AZUL = "#1F3864"      # títulos, anotaciones
AZUL2 = "#2E5496"     # primera serie / curva principal
ROJO = "#9E2A2B"      # segunda serie / filtraciones / shocks
DORADO = "#C9A227"    # puntos de equilibrio
GRIS = "#B0B7C3"      # rejilla, líneas auxiliares
VERDE = "#3A7D44"     # inyecciones / tercera serie

DPI = 150                    # resolución de PNG en reportes
TAMANO_FIGURA = (9.0, 5.5)   # una figura por escenario en el reporte

# --- Tipografía académica (pedida por Edison, 2026-08-19) ---
# mathtext + STIX: las cadenas $...$ de ejes, leyendas y anotaciones se
# renderizan como matemática de libro SIN depender de una instalación LaTeX
# (funciona headless y cubre π, Δ, ↑ …). Poner USAR_TEX_COMPLETO = True para
# usar el LaTeX real del sistema (más lento; requiere TeX Live instalado).
USAR_TEX_COMPLETO = False


def aplicar_estilo():
    """Aplica la identidad tipográfica del laboratorio a matplotlib (global)."""
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "STIX Two Text", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11.5,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })
    if USAR_TEX_COMPLETO:
        matplotlib.rcParams.update({
            "text.usetex": True,
            "text.latex.preamble": r"\usepackage{amsmath}\usepackage[utf8]{inputenc}",
        })
