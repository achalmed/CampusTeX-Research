# base.py — base reutilizable para simuladores interactivos de teoría económica.
#
# Un MODELO define: parámetros (con rango para el slider), y una función
# `curvas(params) -> dict` que devuelve las series a graficar + el equilibrio.
# La base ofrece dos modos:
#   - interactivo(): ventana matplotlib con sliders (ajustar parámetros en vivo,
#     el gráfico se redibuja). Requiere display.
#   - demo(): headless — renderiza el modelo a varios valores de un parámetro y
#     guarda un PDF comparativo (para verificar sin pantalla / documentar).
#
# Reusable: IS-LM, AD-AS, Solow, oferta-demanda, etc. = solo definir el modelo.

from dataclasses import dataclass, field

import matplotlib
import matplotlib.pyplot as plt


@dataclass
class Parametro:
    nombre: str
    valor: float
    minimo: float
    maximo: float
    paso: float = 0.1
    etiqueta: str = ""


@dataclass
class Modelo:
    nombre: str
    parametros: list                       # list[Parametro]
    curvas: object                         # fn(dict) -> dict con 'lineas' y 'equilibrio'
    xlabel: str = "Producto (Y)"
    ylabel: str = "Tasa de interés (r)"
    notas: str = ""

    def dict_params(self):
        return {p.nombre: p.valor for p in self.parametros}


def _dibujar(ax, modelo, params):
    ax.clear()
    datos = modelo.curvas(params)
    for etq, (x, y, color) in datos["lineas"].items():
        ax.plot(x, y, label=etq, color=color, lw=2)
    eq = datos.get("equilibrio")
    if eq:
        ax.plot([eq[0]], [eq[1]], "o", color="#C9A227", ms=9, zorder=5)
        ax.annotate(f"  ({modelo.xlabel[:1]}*={eq[0]:.1f}, {modelo.ylabel[:1]}*={eq[1]:.2f})",
                    (eq[0], eq[1]), fontsize=9, color="#1F3864", fontweight="bold")
    ax.set_xlabel(modelo.xlabel); ax.set_ylabel(modelo.ylabel)
    ax.set_title(modelo.nombre, color="#1F3864", fontweight="bold", loc="left")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(color="#B0B7C3", alpha=0.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)


def interactivo(modelo):
    """Ventana con sliders (requiere backend interactivo / display)."""
    from matplotlib.widgets import Slider
    n = len(modelo.parametros)
    fig, ax = plt.subplots(figsize=(9, 6))
    plt.subplots_adjust(bottom=0.10 + 0.045 * n)
    sliders = []
    for i, p in enumerate(modelo.parametros):
        eje = plt.axes([0.15, 0.02 + 0.045 * i, 0.7, 0.03])
        s = Slider(eje, p.etiqueta or p.nombre, p.minimo, p.maximo,
                   valinit=p.valor, valstep=p.paso)
        sliders.append((p.nombre, s))

    def actualizar(_):
        params = {nombre: s.val for nombre, s in sliders}
        _dibujar(ax, modelo, params)
        fig.canvas.draw_idle()

    for _, s in sliders:
        s.on_changed(actualizar)
    _dibujar(ax, modelo, modelo.dict_params())
    plt.show()


def demo(modelo, parametro, valores, ruta):
    """Headless: renderiza el modelo a varios valores de `parametro` en una
    grilla y guarda un PDF (demuestra el efecto comparativo de ese parámetro)."""
    matplotlib.use("Agg")
    ncols = min(3, len(valores))
    nrows = (len(valores) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 4 * nrows),
                             squeeze=False)
    base = modelo.dict_params()
    for k, v in enumerate(valores):
        ax = axes[k // ncols][k % ncols]
        params = dict(base, **{parametro: v})
        _dibujar(ax, modelo, params)
        ax.set_title(f"{parametro} = {v}", color="#1F3864", fontweight="bold",
                     loc="left", fontsize=10)
    for k in range(len(valores), nrows * ncols):
        axes[k // ncols][k % ncols].axis("off")
    fig.suptitle(f"{modelo.nombre} — sensibilidad a {parametro}",
                 color="#1F3864", fontweight="bold", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(ruta, bbox_inches="tight"); plt.close(fig)
    return ruta
