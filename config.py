# config.py — laboratorio de macroeconomía computacional (simuladores/).
#
# Todo lo ajustable vive aquí: rutas de salida, paleta y formato de figuras.
# Las libs (base.py, reporte.py) no hardcodean nada de esto.

from pathlib import Path

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
