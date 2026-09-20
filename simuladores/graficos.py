"""simuladores/graficos.py — capa de RENDER del laboratorio (matplotlib).

Todo el dibujo vive aquí: primitivas (_dibujar), colocación AUTOMÁTICA de
etiquetas (anti-solape: las anotaciones buscan la esquina/offset con menos
tinta debajo), dibujo progresivo (hasta_lineas: revela las curvas una a una,
para el recorrido pedagógico de app.py), figura suelta, demo de sensibilidad
y overlay de experimento (E1 → E2). El núcleo (base.py) no importa
matplotlib; la experiencia vive en laboratorio.py y app.py.
"""

import numpy as np
import matplotlib
from matplotlib.figure import Figure

import base
import config

config.aplicar_estilo()          # tipografía académica global (serif + mathtext STIX)

_CAJA = dict(boxstyle="round,pad=0.32", fc="white", ec=config.GRIS, alpha=0.92)


def _simbolo(etiqueta):
    """Símbolo del eje para anotar el equilibrio: 'Producto ($Y$)' → '$Y^*{=}$'.
    Sin símbolo corto entre paréntesis, no se antepone nada (solo el número)."""
    if "(" in etiqueta and ")" in etiqueta:
        s = etiqueta[etiqueta.find("(") + 1:etiqueta.find(")")].strip().strip("$")
        if 0 < len(s) <= 3 and s != "%" and "^" not in s and "*" not in s:
            return f"${s}^*{{=}}$"
    return ""


# --- colocación automática de etiquetas (anti-solape) ----------------------

def _muestras(ax, datos):
    """Puntos de las curvas/barras en coordenadas de PANTALLA, para medir
    cuánta 'tinta' quedaría debajo de una etiqueta candidata."""
    pts = []
    for (x, y, _c) in datos.get("lineas", {}).values():
        xs, ys = np.asarray(x, float), np.asarray(y, float)
        paso = max(1, len(xs) // 80)
        pts.append(np.column_stack([xs[::paso], ys[::paso]]))
    b = datos.get("barras")
    if b:
        _cats, vals, _cols = b
        pts.append(np.column_stack([np.arange(len(vals), dtype=float),
                                    np.asarray(vals, float)]))
    if not pts:
        return np.empty((0, 2))
    return ax.transData.transform(np.vstack(pts))


def _rect_libre(rect, muestras, bb, ocupados=()):
    """Puntaje de una caja candidata: muestras que tapa + castigo por salirse
    del eje + castigo fuerte por pisar etiquetas ya colocadas."""
    x0, y0, x1, y1 = rect
    dentro = 0
    if len(muestras):
        m = muestras
        dentro = int(np.sum((m[:, 0] >= x0) & (m[:, 0] <= x1)
                            & (m[:, 1] >= y0) & (m[:, 1] <= y1)))
    fuera = 0
    if x0 < bb.x0 or y0 < bb.y0 or x1 > bb.x1 or y1 > bb.y1:
        fuera = 10_000
    choque = sum(500 for (a0, b0, a1, b1) in ocupados
                 if not (x1 < a0 or a1 < x0 or y1 < b0 or b1 < y0))
    return dentro + fuera + choque


def _anotar_punto(ax, xy, texto, muestras, fontsize=9, color=None, peso="bold"):
    """Anota un punto eligiendo el offset (8 candidatos) que menos tape: evita
    curvas, bordes y las etiquetas YA colocadas en este eje (memoria en ax)."""
    color = color or config.AZUL
    ocupados = getattr(ax, "_lab_ocupados", None)
    if ocupados is None:
        ocupados = ax._lab_ocupados = []
    dpi = ax.figure.dpi
    px, py = ax.transData.transform(xy)
    ancho = 0.56 * fontsize * dpi / 72 * max(4, len(texto.replace("$", "")))
    alto = 1.5 * fontsize * dpi / 72
    bb = ax.get_window_extent()
    candidatos = [(10, 9, "left"), (10, -9 - alto * 0.6, "left"),
                  (-10, 9, "right"), (-10, -9 - alto * 0.6, "right"),
                  (0, 14 + alto * 0.5, "center"), (0, -14 - alto * 0.8, "center"),
                  (16, 0, "left"), (-16, 0, "right")]
    mejor, mejor_rect, mejor_p = None, None, None
    for dx, dy, ha in candidatos:
        x0 = {"left": px + dx, "right": px + dx - ancho,
              "center": px + dx - ancho / 2}[ha]
        rect = (x0, py + dy - alto / 2, x0 + ancho, py + dy + alto / 2)
        puntaje = _rect_libre(rect, muestras, bb, ocupados)
        if mejor_p is None or puntaje < mejor_p:
            mejor_p, mejor, mejor_rect = puntaje, (dx, dy, ha), rect
    dx, dy, ha = mejor
    ocupados.append(mejor_rect)
    ax.annotate(texto, xy, textcoords="offset pixels", xytext=(dx, dy),
                ha=ha, va="center", fontsize=fontsize, color=color,
                fontweight=peso, bbox=_CAJA, zorder=7)


def _mejor_esquina(ax, muestras):
    """Esquina del axes con menos tinta debajo, para la caja de anotación."""
    bb = ax.get_window_extent()
    w, h = 0.40 * bb.width, 0.26 * bb.height
    esquinas = [((0.02, 0.98), "left", "top", (bb.x0, bb.y1 - h, bb.x0 + w, bb.y1)),
                ((0.98, 0.98), "right", "top", (bb.x1 - w, bb.y1 - h, bb.x1, bb.y1)),
                ((0.02, 0.02), "left", "bottom", (bb.x0, bb.y0, bb.x0 + w, bb.y0 + h)),
                ((0.98, 0.02), "right", "bottom", (bb.x1 - w, bb.y0, bb.x1, bb.y0 + h))]
    mejor = min(esquinas, key=lambda e: _rect_libre(e[3], muestras, bb))
    (fx, fy), ha, va, _ = mejor
    return fx, fy, ha, va


# --- primitiva principal ---------------------------------------------------

def _dibujar(ax, modelo, params, hasta_lineas=None, con_equilibrio=True,
             con_puntos=True, con_anotacion=True, con_leyenda=True):
    """Dibuja el modelo. `hasta_lineas=i` revela solo las primeras i curvas
    (construcción progresiva); los demás flags apagan capas para el recorrido."""
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

    lineas = list(datos.get("lineas", {}).items())
    if hasta_lineas is not None:
        lineas = lineas[:hasta_lineas]
    for etq, (x, y, color) in lineas:
        ax.plot(x, y, label=etq, color=color, lw=2)

    # los límites deben estar fijados ANTES de medir solapes en pantalla
    ax.relim(); ax.autoscale_view()
    muestras = _muestras(ax, datos)
    ax._lab_ocupados = []          # memoria de etiquetas colocadas en este eje

    if con_puntos:
        for (px, py, etq) in datos.get("puntos", []):
            ax.plot([px], [py], "o", color=config.DORADO, ms=8, zorder=5)
            _anotar_punto(ax, (px, py), etq, muestras)
    eq = datos.get("equilibrio")
    if eq and con_equilibrio:
        ax.plot([eq[0]], [eq[1]], "o", color=config.DORADO, ms=9, zorder=6)
        sx, sy = _simbolo(modelo.xlabel), _simbolo(modelo.ylabel)
        _anotar_punto(ax, eq, f"({sx}{eq[0]:.1f}, {sy}{eq[1]:.2f})", muestras)
    if datos.get("anotacion") and con_anotacion:
        fx, fy, ha, va = _mejor_esquina(ax, muestras)
        ax.text(fx, fy, datos["anotacion"], transform=ax.transAxes,
                va=va, ha=ha, fontsize=9, color=config.AZUL, bbox=_CAJA, zorder=8)

    ax.set_xlabel(modelo.xlabel); ax.set_ylabel(modelo.ylabel)
    ax.set_title(modelo.nombre, color=config.AZUL, fontweight="bold", loc="left")
    if lineas and con_leyenda:
        ax.legend(frameon=False, loc="best")
    ax.grid(color=config.GRIS, alpha=0.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    return datos


def marcar_transicion(ax, modelo, params_antes, params_despues):
    """Overlay de experimento: marca E1 (hueco) y la flecha E1 → E2 cuando
    ambos estados declaran un equilibrio distinto. E2 ya lo dibuja _dibujar."""
    datos1 = modelo.curvas(params_despues)
    e0 = modelo.curvas(params_antes).get("equilibrio")
    e1 = datos1.get("equilibrio")
    if not e0 or not e1 or (abs(e0[0] - e1[0]) + abs(e0[1] - e1[1])) < 1e-9:
        return False
    muestras = _muestras(ax, datos1)
    ax.plot([e0[0]], [e0[1]], "o", mfc="white", mec=config.DORADO, mew=1.8,
            ms=9, zorder=6)
    _anotar_punto(ax, e0, "$E_1$", muestras, fontsize=10)
    _anotar_punto(ax, e1, "$E_2$", muestras, fontsize=10)
    ax.annotate("", xy=e1, xytext=e0,
                arrowprops=dict(arrowstyle="-|>", color=config.AZUL, lw=1.6,
                                shrinkA=8, shrinkB=8))
    return True


def figura(modelo, params=None, titulo=None):
    """Figura suelta (sin pyplot: no toca el backend ni las ventanas abiertas)."""
    fig = Figure(figsize=config.TAMANO_FIGURA)
    ax = fig.add_subplot()
    _dibujar(ax, modelo, params or modelo.dict_params())
    if titulo:
        ax.set_title(f"{modelo.nombre} — {titulo}", color=config.AZUL,
                     fontweight="bold", loc="left")
    fig.tight_layout()
    return fig


def figura_sensibilidad(modelo, sens):
    """Gráfico del análisis de sensibilidad (base.sensibilidad) — magnitud vs parámetro."""
    fig = Figure(figsize=(7.5, 4.8))
    ax = fig.add_subplot()
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
    ncols = min(3, len(valores))
    nrows = (len(valores) + ncols - 1) // ncols
    fig = Figure(figsize=(5.5 * ncols, 4 * nrows))
    axes = fig.subplots(nrows, ncols, squeeze=False)
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
    fig.savefig(ruta, bbox_inches="tight")
    return ruta
