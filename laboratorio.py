# laboratorio.py — capa de EXPERIENCIA del laboratorio.
#
# Convierte "sliders + gráfico" en experimentación económica (observación de
# Edison, 2026-08-19). Dos entregas:
#
#   lamina(modelo, escenario, ruta)  — hoja de experimento de 5 zonas, headless:
#       ┌ CONTEXTO: modelo · nivel · pregunta económica · experimento
#       ├ GRÁFICO con E1 → E2 (flecha de transición)   ├ RESULTADOS (tabla Δ)
#       ├ MECANISMO de transmisión (cadena causal)     ├ ECUACIONES calibradas
#       └ LECTURA económica ("¿por qué ocurrió esto?")
#     Se incrusta en el reporte MD de cada escenario: cada experimento queda
#     documentado como página de laboratorio, no como gráfico suelto.
#
#   laboratorio(modelo)  — modo interactivo: selector de escenarios (radio),
#     el gráfico, la tabla y el mecanismo se actualizan al elegir experimento.
#     El modo de sliders clásico sigue disponible (interactivo()) como
#     "modo avanzado" para tocar parámetros libres.

import textwrap

import matplotlib
import matplotlib.pyplot as plt

import base
import config
import graficos


def _wrap(texto, ancho):
    return "\n".join(textwrap.wrap(texto, ancho))


def _filas_delta(modelo, esc, maximo=9):
    res0, res1 = modelo.calcular(), modelo.calcular(**esc.cambios)
    filas = []
    for k, v0 in res0.items():
        v1 = res1.get(k)
        if isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
            filas.append((k, base.fmt(v0), base.fmt(v1),
                          f"{base.signo(v1 - v0)} {base.fmt(abs(v1 - v0))}"))
    if len(filas) > maximo:
        filas = filas[:maximo] + [("…", "", "", "")]
    return filas


def _texto_mecanismo(esc, ancho=52):
    if esc.cadena:
        pasos = "  →  ".join(esc.cadena)
        return _wrap(pasos, ancho)
    return _wrap(esc.lectura, ancho) if esc.lectura else "(mecanismo no declarado aún)"


def _math_seguro(latex):
    """Adapta LaTeX de ficha (pensado para MathJax) al subconjunto mathtext de
    matplotlib; devuelve '$...$' o None si la línea no es renderizable."""
    s = (latex.replace("\\Big", "").replace("\\big", "")
              .replace("\\boxed", "").replace("\\text{", "\\mathrm{"))
    linea = s if s.startswith("$") else f"${s}$"
    try:
        from matplotlib.mathtext import MathTextParser
        MathTextParser("path").parse(linea, dpi=72)
        return linea
    except Exception:
        return None


def _texto_ecuaciones(modelo, params, maximo=4):
    if modelo.ecuaciones_calibradas:
        candidatas = modelo.ecuaciones_calibradas(params)
    elif modelo.ficha and modelo.ficha.ecuaciones:
        candidatas = [e.latex for e in modelo.ficha.ecuaciones]
    else:
        return ""
    lineas = [m for m in (_math_seguro(c) for c in candidatas) if m][:maximo]
    return "\n".join(lineas)


def _panel_texto(ax, titulo, cuerpo, tam=9.5):
    ax.axis("off")
    ax.text(0.0, 1.0, titulo, transform=ax.transAxes, va="top", ha="left",
            fontsize=10.5, color=config.AZUL, fontweight="bold")
    ax.text(0.0, 0.80, cuerpo, transform=ax.transAxes, va="top", ha="left",
            fontsize=tam, color="#222222", linespacing=1.55)


def _tabla_resultados(ax, filas):
    ax.axis("off")
    ax.text(0.0, 1.0, "RESULTADOS", transform=ax.transAxes, va="top",
            fontsize=10.5, color=config.AZUL, fontweight="bold")
    tabla = ax.table(cellText=[list(f) for f in filas],
                     colLabels=["magnitud", "base", "experimento", "Δ"],
                     colWidths=[0.46, 0.18, 0.18, 0.18],
                     loc="upper left", bbox=[0.0, 0.0, 1.0, 0.86])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.6)
    for (fila, col), celda in tabla.get_celld().items():
        celda.set_edgecolor(config.GRIS)
        celda.set_linewidth(0.5)
        if fila == 0:
            celda.set_text_props(color="white", fontweight="bold")
            celda.set_facecolor(config.AZUL)
        elif col == 0:
            celda.set_text_props(ha="left")
            celda.PAD = 0.03


def _componer(fig, modelo, esc):
    """Dibuja las 5 zonas del experimento sobre una figura (lámina o ventana)."""
    fig.clf()
    params0 = modelo.dict_params()
    params1 = dict(params0, **esc.cambios) if esc else dict(params0)

    # ── zona A: contexto ────────────────────────────────────────────────────
    F = modelo.ficha
    fig.text(0.035, 0.975, "LABORATORIO MACROECONÓMICO",
             fontsize=9.5, color=config.GRIS, fontweight="bold")
    fig.text(0.035, 0.945, f"{modelo.nombre}  ·  nivel {modelo.nivel}  ·  {modelo.id}",
             fontsize=15, color=config.AZUL, fontweight="bold")
    y = 0.915
    if F and F.pregunta:
        fig.text(0.035, y, _wrap(f"Pregunta: {F.pregunta}", 110),
                 fontsize=10.5, color="#222222", style="italic")
        y -= 0.030
    if esc:
        cambios = ", ".join(f"{k}: {base.fmt(modelo.parametro(k).valor)} → {base.fmt(v)}"
                            for k, v in esc.cambios.items())
        fig.text(0.035, y, f"🧪 Experimento «{esc.nombre}»: {esc.descripcion}  ({cambios})",
                 fontsize=10.5, color=config.ROJO)

    gs = fig.add_gridspec(nrows=2, ncols=2, left=0.055, right=0.97,
                          top=0.855, bottom=0.135,
                          width_ratios=[3.1, 2.0], height_ratios=[3.2, 1.35],
                          hspace=0.42, wspace=0.16)

    # ── zona B: gráfico con E1 → E2 ─────────────────────────────────────────
    ax_g = fig.add_subplot(gs[0, 0])
    graficos._dibujar(ax_g, modelo, params1)
    if esc:
        graficos.marcar_transicion(ax_g, modelo, params0, params1)

    # ── zona C: resultados (tabla Δ) ────────────────────────────────────────
    ax_r = fig.add_subplot(gs[0, 1])
    if esc:
        _tabla_resultados(ax_r, _filas_delta(modelo, esc))
    else:
        res = modelo.calcular()
        filas = [(k, base.fmt(v), "", "") for k, v in res.items()
                 if isinstance(v, (int, float))][:9]
        _tabla_resultados(ax_r, filas)

    # ── zona D: mecanismo de transmisión ────────────────────────────────────
    ax_m = fig.add_subplot(gs[1, 0])
    _panel_texto(ax_m, "MECANISMO DE TRANSMISIÓN",
                 _texto_mecanismo(esc) if esc else "(elige un experimento)", tam=10)

    # ── zona E: ecuaciones vigentes ─────────────────────────────────────────
    ax_e = fig.add_subplot(gs[1, 1])
    _panel_texto(ax_e, "ECUACIONES (valores vigentes)",
                 _texto_ecuaciones(modelo, params1), tam=10)

    # ── pie: lectura económica ("¿por qué?") ────────────────────────────────
    if esc and esc.lectura:
        fig.text(0.035, 0.020, _wrap(f"¿Por qué?  {esc.lectura}", 130),
                 fontsize=9.5, color="#333333")


def lamina(modelo, esc, ruta):
    """Hoja de experimento (headless): las 5 zonas en un PNG para el reporte."""
    matplotlib.use("Agg")
    fig = plt.figure(figsize=(13.0, 8.6))
    _componer(fig, modelo, esc)
    fig.savefig(ruta, dpi=config.DPI)
    plt.close(fig)
    return ruta


def laboratorio(modelo):
    """Modo laboratorio interactivo: elegir experimento → ver mecanismo,
    resultados y transición E1→E2. Requiere display."""
    from matplotlib.widgets import RadioButtons
    fig = plt.figure(figsize=(13.0, 8.6))
    esc_inicial = modelo.escenarios[0] if modelo.escenarios else None
    _componer(fig, modelo, esc_inicial)

    nombres = ["(base)"] + [e.nombre for e in modelo.escenarios]
    ax_radio = fig.add_axes([0.035, 0.06, 0.16, 0.010 + 0.030 * len(nombres)])
    ax_radio.set_title("Experimento", fontsize=9, color=config.AZUL, loc="left")
    radio = RadioButtons(ax_radio, nombres,
                         active=1 if esc_inicial else 0)

    def _elegir(nombre):
        esc = None if nombre == "(base)" else modelo.escenario(nombre)
        _componer(fig, modelo, esc)
        # el gridspec se recompone: recolocar el selector encima
        fig.add_axes(ax_radio)
        fig.canvas.draw_idle()

    radio.on_clicked(_elegir)
    plt.show()


def interactivo(modelo):
    """Modo avanzado clásico: sliders libres sobre todos los parámetros."""
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
        graficos._dibujar(ax, modelo, params)
        fig.canvas.draw_idle()

    for _, s in sliders:
        s.on_changed(actualizar)
    graficos._dibujar(ax, modelo, modelo.dict_params())
    plt.show()
