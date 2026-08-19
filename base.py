# base.py — núcleo del laboratorio de macroeconomía computacional.
#
# Un modelo del laboratorio une tres capas (diseño: docs/LABORATORIO_MACRO.md):
#
#   1. FICHA PEDAGÓGICA (Ficha): contexto histórico, autores/escuelas, supuestos,
#      ecuaciones explicadas una a una, intuición, equilibrio, limitaciones y
#      evolución (qué modelo lo supera y por qué). Es el "por qué" del modelo.
#   2. MOTOR NUMÉRICO: curvas(params) -> dict con lo graficable, y
#      resultados(params) -> dict con las magnitudes de equilibrio. El "cómo".
#   3. CONTRATOS DE CALIDAD: escenarios (experimentos nombrados con lectura
#      económica) y verificaciones (chequeos numéricos: las identidades
#      contables se exigen EXACTAS, las convergencias con tolerancia).
#
# curvas(params) devuelve un dict con claves opcionales:
#   "lineas":     {etiqueta: (x, y, color)}
#   "barras":     (categorias, valores, colores)      — una serie de barras
#   "puntos":     [(x, y, etiqueta)]                  — puntos destacados
#   "equilibrio": (x, y)                              — punto de equilibrio
#   "anotacion":  str                                 — texto en la esquina
#
# Modos de uso: interactivo() (sliders, requiere display), demo() (PDF headless
# de sensibilidad), y reporte.py (informe MD con figuras por escenario).
# Compatible con modelos antiguos: todos los campos nuevos tienen default.

from dataclasses import dataclass, field

import matplotlib
import matplotlib.pyplot as plt

import config

config.aplicar_estilo()          # tipografía académica global (serif + mathtext STIX)


@dataclass
class Parametro:
    nombre: str
    valor: float
    minimo: float
    maximo: float
    paso: float = 0.1
    etiqueta: str = ""


@dataclass
class Ecuacion:
    latex: str          # p.ej. "C = C_0 + c \\, Y_d"
    nombre: str         # p.ej. "función de consumo"
    significado: str    # de dónde surge y qué representa cada término


@dataclass
class Ficha:
    """Ficha pedagógica estándar: el modelo como episodio de la historia del
    pensamiento macroeconómico, no solo como sistema de ecuaciones."""
    contexto: str                    # contexto histórico y problema que intentaba explicar
    autores: str                     # autores, años y escuelas de pensamiento
    supuestos: list                  # list[str] — supuestos teóricos explícitos
    ecuaciones: list                 # list[Ecuacion] — construcción paso a paso
    intuicion: str                   # la intuición económica detrás de las ecuaciones
    equilibrio: str = ""             # condición de equilibrio y estabilidad
    limitaciones: list = field(default_factory=list)   # críticas y problemas empíricos
    evolucion: str = ""              # qué modelo del currículo lo supera y por qué
    procedencia: str = "conocimiento macroeconómico general (manuales estándar de macro intermedia); NO verificado contra edición específica"
    referencias: list = field(default_factory=list)


@dataclass
class Escenario:
    nombre: str         # clave para la CLI (sin espacios)
    descripcion: str    # qué experimento es ("aumento del gasto público en 100")
    cambios: dict       # {parametro: nuevo_valor}
    lectura: str = ""   # interpretación económica del resultado esperado


@dataclass
class Verificacion:
    nombre: str
    fn: object          # fn() -> (bool, str detalle)


@dataclass
class Modelo:
    nombre: str
    parametros: list                       # list[Parametro]
    curvas: object                         # fn(dict) -> dict (ver cabecera)
    xlabel: str = "Producto ($Y$)"
    ylabel: str = "Tasa de interés ($r$)"
    notas: str = ""
    # --- capas del laboratorio (todas opcionales para compatibilidad) ---
    id: str = ""                           # posición curricular ("m03")
    nivel: int = 0                         # nivel del currículo (1..12)
    ficha: object = None                   # Ficha
    escenarios: list = field(default_factory=list)      # list[Escenario]
    resultados: object = None              # fn(dict) -> dict[str, float]
    verificaciones: list = field(default_factory=list)  # list[Verificacion]

    def dict_params(self):
        return {p.nombre: p.valor for p in self.parametros}

    def escenario(self, nombre):
        for e in self.escenarios:
            if e.nombre == nombre:
                return e
        raise KeyError(f"escenario '{nombre}' no existe en {self.id or self.nombre} "
                       f"(disponibles: {', '.join(e.nombre for e in self.escenarios) or 'ninguno'})")

    def calcular(self, **cambios):
        """Resultados del modelo con los parámetros por defecto más `cambios`."""
        params = dict(self.dict_params(), **cambios)
        if self.resultados:
            return self.resultados(params)
        eq = self.curvas(params).get("equilibrio")
        return {"x*": eq[0], "y*": eq[1]} if eq else {}


def fmt(v):
    """Formato legible para magnitudes económicas (miles con coma, decimales cortos)."""
    if not isinstance(v, (int, float)):
        return str(v)
    if abs(v) >= 1000:
        return f"{v:,.1f}"
    if abs(v) >= 10:
        return f"{v:.1f}"
    if abs(v) >= 1:
        return f"{v:.2f}"
    return f"{v:.3f}"


def _simbolo(etiqueta):
    """Símbolo del eje para anotar el equilibrio: 'Producto ($Y$)' → '$Y^*{=}$'.
    Sin símbolo corto entre paréntesis, no se antepone nada (solo el número)."""
    if "(" in etiqueta and ")" in etiqueta:
        s = etiqueta[etiqueta.find("(") + 1:etiqueta.find(")")].strip().strip("$")
        if 0 < len(s) <= 3 and s != "%":
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
            ax.annotate(fmt(v), (i, v), ha="center", fontsize=9,
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
        ax.set_title(f"{parametro} = {v}", color=config.AZUL, fontweight="bold",
                     loc="left", fontsize=10)
    for k in range(len(valores), nrows * ncols):
        axes[k // ncols][k % ncols].axis("off")
    fig.suptitle(f"{modelo.nombre} — sensibilidad a {parametro}",
                 color=config.AZUL, fontweight="bold", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(ruta, bbox_inches="tight"); plt.close(fig)
    return ruta


def verificar(modelo):
    """Corre las verificaciones del modelo; devuelve [(nombre, ok, detalle)]."""
    salida = []
    for v in modelo.verificaciones:
        try:
            ok, detalle = v.fn()
        except Exception as exc:            # una verificación que revienta = fallo
            ok, detalle = False, f"excepción: {exc}"
        salida.append((v.nombre, bool(ok), detalle))
    return salida
