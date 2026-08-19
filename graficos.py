# graficos.py — capa de RENDER del laboratorio (matplotlib).
#
# Todo el dibujo vive aquí: primitivas (_dibujar), figura suelta, demo de
# sensibilidad y overlay de experimento (E1 → E2). El núcleo (base.py) no
# importa matplotlib; la experiencia interactiva vive en laboratorio.py.

import matplotlib
import matplotlib.pyplot as plt

import base
import config

config.aplicar_estilo()          # tipografía académica global (serif + mathtext STIX)


def _simbolo(etiqueta):
    """Símbolo del eje para anotar el equilibrio: 'Producto ($Y$)' → '$Y^*{=}$'.
    Sin símbolo corto entre paréntesis, no se antepone nada (solo el número)."""
    if "(" in etiqueta and ")" in etiqueta:
        s = etiqueta[etiqueta.find("(") + 1:etiqueta.find(")")].strip().strip("$")
        if 0 < len(s) <= 3 and s != "%" and "^" not in s and "*" not in s:
            return f"${s}^*{{=}}$"
    return ""


def _dibujar(ax, modelo, params):
    ax.clear()
    datos = modelo.curvas(params)
    barras = datos.get("barras")
    if barras:
        cats, vals, cols = barras
        pos = range(len(cats))
        ax.bar(pos, vals, color=cols, width=0.62)
        ax.set_xticks(list(pos))
        ax.set_xticklabels(cats)
        for i, v in enumerate(vals):
            ax.annotate(base.fmt(v), (i, v), ha="center", fontsize=9,
                        va="bottom" if v >= 0 else "top", color=config.AZUL)
        ax.axhline(0, color=config.GRIS, lw=0.8)
    for etq, (x, y, color) in datos.get("lineas", {}).items():
        ax.plot(x, y, label=etq, color=color, lw=2)
    for (px, py, etq) in datos.get("puntos", []):
        ax.plot([px], [py], "o", color=config.DORADO, ms=8, zorder=5)
        ax.annotate(f"  {etq}", (px, py), fontsize=9, color=config.AZUL,
                    fontweight="bold")
    eq = datos.get("equilibrio")
    if eq:
        ax.plot([eq[0]], [eq[1]], "o", color=config.DORADO, ms=9, zorder=5)
        sx, sy = _simbolo(modelo.xlabel), _simbolo(modelo.ylabel)
        ax.annotate(f"  ({sx}{eq[0]:.1f}, {sy}{eq[1]:.2f})",
                    (eq[0], eq[1]), fontsize=9, color=config.AZUL, fontweight="bold")
    if datos.get("anotacion"):
        ax.text(0.02, 0.98, datos["anotacion"], transform=ax.transAxes,
                va="top", ha="left", fontsize=9, color=config.AZUL,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=config.GRIS, alpha=0.9))
    ax.set_xlabel(modelo.xlabel); ax.set_ylabel(modelo.ylabel)
    ax.set_title(modelo.nombre, color=config.AZUL, fontweight="bold", loc="left")
    if datos.get("lineas"):
        ax.legend(frameon=False, loc="best")
    ax.grid(color=config.GRIS, alpha=0.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)


def marcar_transicion(ax, modelo, params_antes, params_despues):
    """Overlay de experimento: marca E1 (hollow) y la flecha E1 → E2 cuando
    ambos estados declaran un equilibrio distinto. E2 ya lo dibuja _dibujar."""
    e0 = modelo.curvas(params_antes).get("equilibrio")
    e1 = modelo.curvas(params_despues).get("equilibrio")
    if not e0 or not e1 or (abs(e0[0] - e1[0]) + abs(e0[1] - e1[1])) < 1e-9:
        return False
    ax.plot([e0[0]], [e0[1]], "o", mfc="white", mec=config.DORADO, mew=1.8,
            ms=9, zorder=6)
    ax.annotate("$E_1$", e0, textcoords="offset points", xytext=(-14, -14),
                fontsize=10, color=config.AZUL, fontweight="bold")
    ax.annotate("$E_2$", e1, textcoords="offset points", xytext=(6, 8),
                fontsize=10, color=config.AZUL, fontweight="bold")
    ax.annotate("", xy=e1, xytext=e0,
                arrowprops=dict(arrowstyle="-|>", color=config.AZUL, lw=1.6,
                                shrinkA=8, shrinkB=8))
    return True


def figura(modelo, params=None, titulo=None):
    """Figura suelta (headless) del modelo con `params`; para reporte.py."""
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=config.TAMANO_FIGURA)
    _dibujar(ax, modelo, params or modelo.dict_params())
    if titulo:
        ax.set_title(f"{modelo.nombre} — {titulo}", color=config.AZUL,
                     fontweight="bold", loc="left")
    fig.tight_layout()
    return fig


def figura_sensibilidad(modelo, sens):
    """Gráfico del análisis de sensibilidad (base.sensibilidad) — magnitud vs parámetro."""
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    xs = [f[0] for f in sens["filas"]]; ys = [f[1] for f in sens["filas"]]
    ax.plot(xs, ys, "o-", color=config.AZUL2, lw=2, ms=5)
    ax.axvline(sens["base"], color=config.GRIS, lw=1, ls="--")
    ax.set_xlabel(f"parámetro {sens['parametro']}")
    ax.set_ylabel(sens["magnitud"])
    ax.set_title(f"{modelo.nombre} — sensibilidad "
                 f"($\\partial/\\partial {sens['parametro']} = {sens['derivada']:.3f}$ en la base)",
                 color=config.AZUL, fontweight="bold", loc="left", fontsize=11)
    ax.grid(color=config.GRIS, alpha=0.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def demo(modelo, parametro, valores, ruta):
    """Headless: renderiza el modelo a varios valores de `parametro` en una
    grilla y guarda un PDF (demuestra el efecto comparativo de ese parámetro)."""
    matplotlib.use("Agg")
    ncols = min(3, len(valores))
    nrows = (len(valores) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 4 * nrows),
                             squeeze=False)
    base_p = modelo.dict_params()
    for k, v in enumerate(valores):
        ax = axes[k // ncols][k % ncols]
        params = dict(base_p, **{parametro: v})
        _dibujar(ax, modelo, params)
        ax.set_title(f"{parametro} = {v}", color=config.AZUL, fontweight="bold",
                     loc="left", fontsize=10)
    for k in range(len(valores), nrows * ncols):
        axes[k // ncols][k % ncols].axis("off")
    fig.suptitle(f"{modelo.nombre} — sensibilidad a {parametro}",
                 color=config.AZUL, fontweight="bold", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(ruta, bbox_inches="tight"); plt.close(fig)
    return ruta
