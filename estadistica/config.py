"""simuladores/estadistica/config.py — laboratorio de estadística computacional (simuladores/estadistica/).

El "config" de esta disciplina (patrón config-por-proyecto): rutas propias +
paleta y estilo del laboratorio. El motor compartido de la raíz (graficos.py,
reporte.py) hace `import config` y resuelve a ESTE cuando la disciplina está
primera en el sys.path — así comparte el motor sin hardcodear nada.
"""

import os
from pathlib import Path

import matplotlib

# Plasma/Wayland: xcb (X11) es el fallback estable para los modos interactivos.
if os.environ.get("WAYLAND_DISPLAY") and "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

DIR_BASE = Path(__file__).resolve().parent           # simuladores/estadistica
DIR_MODELOS = DIR_BASE / "modelos"
DIR_SALIDAS = DIR_BASE / "salidas"                   # reportes/figuras (regenerable, .gitignore)

# Paleta del laboratorio (idéntica al macro — identidad visual común)
AZUL = "#1F3864"      # títulos, anotaciones
AZUL2 = "#2E5496"     # primera serie / curva principal
ROJO = "#9E2A2B"      # segunda serie / valores atípicos / shocks
DORADO = "#C9A227"    # curva teórica / puntos clave
GRIS = "#B0B7C3"      # rejilla, líneas auxiliares
VERDE = "#3A7D44"     # tercera serie / población

DPI = 150
TAMANO_FIGURA = (9.0, 5.5)

# Secciones del currículo (nivel → nombre), para `listar` y la app.
SECCIONES = {
    1: "I · Fundamentos: datos y medición",
    2: "II · Estadística descriptiva",
    3: "III · Probabilidad",
    4: "IV · Distribuciones de probabilidad",
    5: "V · Teoremas fundamentales",
    6: "VI · Muestreo",
    7: "VII · Inferencia estadística",
    8: "VIII · Pruebas de hipótesis",
    9: "IX · Pruebas no paramétricas",
    10: "X · Correlación y asociación",
    11: "XI · Regresión estadística",
    12: "XII · Diagnóstico de modelos",
    13: "XIII · Máxima verosimilitud",
    14: "XIV · Métodos bayesianos",
    15: "XV · Bootstrap y simulación",
    16: "XVI · Multivariante",
    17: "XVII · Series temporales",
    18: "XVIII · Estadística espacial",
    19: "XIX · Estadística causal",
    20: "XX · Computacional y ML",
}

# Etiquetas de la app compartida (simuladores/app.py las lee por disciplina)
APP_VENTANA = "Laboratorio de Estadística Computacional"
APP_NOMBRE = "LABORATORIO DE ESTADÍSTICA COMPUTACIONAL"
APP_TITULO = "Laboratorio Interactivo de Estadística"
APP_RECORRIDO = ("Elige un tema y recórrelo: pregunta → derivación → simulación → "
                 "resultados → experimentos.  (↑/↓ y Enter)")
APP_UNIDAD_NIVEL = "Sección"
APP_PASO_RESULTADOS = "Resultados y propiedades"
APP_PANEL_RESULTADOS = "PROPIEDADES"
APP_PASO_COMPARACION = "Comparación de escenarios"

USAR_TEX_COMPLETO = False


def aplicar_estilo():
    """Identidad tipográfica del laboratorio (serif + mathtext STIX), global."""
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
