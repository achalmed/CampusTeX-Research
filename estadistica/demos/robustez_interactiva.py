# robustez_interactiva.py — DEMO de la capa INTERACTIVA EN VIVO (matplotlib).
#
# Responde a la pregunta de Edison: "¿puedo ver las animaciones EN EL PROYECTO
# sin reproducir un video?". SÍ — esto es matplotlib, no Manim: se ejecuta y
# abre una VENTANA INTERACTIVA. Mueve el slider (o arrastra) y observa EN VIVO
# cómo un solo dato extremo ARRASTRA la media pero casi no mueve la mediana
# (robustez; sección II, temas 32-33). No hay ningún archivo de video: la
# animación ocurre en la app, en tiempo real, respondiendo a ti.
#
#   Manim  → genera un VIDEO pulido (para redes / incrustar).
#   ESTO   → interactividad EN VIVO dentro del proyecto (para explorar/aprender).
#
# Ejecutar (en un entorno con ventana):
#   python3 robustez_interactiva.py
#
# (Este archivo es una DEMOSTRACIÓN del concepto; la versión final vivirá como la
#  vista interactiva del modelo de descriptiva del lab, alimentada por base.py.)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Paleta del laboratorio (misma que simuladores/config.py)
AZUL = "#2E5496"; DORADO = "#C9A227"; ROJO = "#9E2A2B"; GRIS = "#B0B7C3"; VERDE = "#3A7D44"

DATOS_BASE = np.array([4, 5, 5, 6, 6, 6, 7, 7, 8], float)   # 9 datos "normales"


def _stack_y(datos):
    """Apila puntos repetidos (dotplot): y = 0,1,2,… para valores iguales."""
    y, vistos = [], {}
    for v in datos:
        vistos[v] = vistos.get(v, 0)
        y.append(vistos[v])
        vistos[v] += 1
    return np.array(y, float)


def estadisticos(outlier):
    x = np.append(DATOS_BASE, outlier)
    return x, float(x.mean()), float(np.median(x)), float(x.std())


def dibujar(ax, outlier):
    ax.clear()
    x, media, mediana, sd = estadisticos(outlier)

    # dotplot: los 9 datos base + el dato extremo (rojo)
    yb = _stack_y(DATOS_BASE)
    ax.scatter(DATOS_BASE, yb, s=260, color=VERDE, edgecolor="white", zorder=3)
    ax.scatter([outlier], [0], s=320, color=ROJO, edgecolor="white", zorder=4)
    ax.annotate("dato extremo", (outlier, 0), textcoords="offset points",
                xytext=(0, 16), ha="center", color=ROJO, fontsize=10, fontweight="bold")

    # media (arrastrada) y mediana (robusta) como líneas verticales
    ax.axvline(media, color=AZUL, lw=2.5, label=f"media = {media:.2f}")
    ax.axvline(mediana, color=DORADO, lw=2.5, ls="--", label=f"mediana = {mediana:.2f}")
    # banda ±1 desviación estándar alrededor de la media
    ax.axvspan(media - sd, media + sd, color=AZUL, alpha=0.08,
               label=f"±1 desv. est. = {sd:.2f}")

    ax.set_xlim(-1, 31)
    ax.set_ylim(-0.8, 4)
    ax.set_yticks([])
    ax.set_xlabel("valor del dato")
    ax.set_title("Robustez: un dato extremo mueve la MEDIA, no la MEDIANA",
                 color=AZUL, fontweight="bold", loc="left")
    ax.legend(loc="upper right", framealpha=0.95)
    ax.grid(axis="x", color=GRIS, alpha=0.3)
    ax.spines[["top", "right", "left"]].set_visible(False)


def main():
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    plt.subplots_adjust(bottom=0.22)
    dibujar(ax, 8.0)

    eje_slider = plt.axes([0.15, 0.08, 0.70, 0.04])
    slider = Slider(eje_slider, "dato extremo", 0.0, 30.0, valinit=8.0,
                    color=ROJO, valstep=0.5)
    slider.on_changed(lambda val: (dibujar(ax, val), fig.canvas.draw_idle()))

    plt.show()


if __name__ == "__main__":
    main()
