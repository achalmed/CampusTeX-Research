# reporte.py — informe Markdown por modelo del laboratorio.
#
# Renderiza la ficha pedagógica completa + resultados base + una tabla y una
# figura por escenario + el resultado de las verificaciones. La salida va a
# salidas/nivel_NN/<id>_<slug>/reporte.md (regenerable; no se versiona).
# El MD usa bloques $$...$$ para las ecuaciones: se lee bien en Obsidian.

import matplotlib.pyplot as plt

import base
import config


def _tabla(filas, cabecera):
    ancho = [max(len(str(f[i])) for f in [cabecera] + filas) for i in range(len(cabecera))]
    def linea(f):
        return "| " + " | ".join(str(c).ljust(a) for c, a in zip(f, ancho)) + " |"
    sep = "|" + "|".join("-" * (a + 2) for a in ancho) + "|"
    return "\n".join([linea(cabecera), sep] + [linea(f) for f in filas])


def _comparacion(base_res, esc_res):
    filas = []
    for k, v0 in base_res.items():
        v1 = esc_res.get(k)
        if not isinstance(v0, (int, float)) or not isinstance(v1, (int, float)):
            continue
        d = v1 - v0
        pct = f"{100 * d / abs(v0):+.1f}%" if abs(v0) > 1e-12 else "—"
        filas.append((k, base.fmt(v0), base.fmt(v1), base.fmt(d), pct))
    return _tabla(filas, ("magnitud", "base", "escenario", "Δ", "Δ%"))


def render(modelo, dir_salidas=None):
    """Genera reporte.md + figuras PNG del modelo. Devuelve la ruta del MD."""
    raiz = dir_salidas or config.DIR_SALIDAS
    slug = f"{modelo.id}_{modelo.nombre}" if modelo.id else modelo.nombre
    slug = slug.lower().replace(" ", "_").replace("—", "-")
    slug = slug.translate(str.maketrans("áéíóúñü", "aeiounu"))
    carpeta = raiz / (f"nivel_{modelo.nivel:02d}" if modelo.nivel else "sin_nivel") / slug
    carpeta.mkdir(parents=True, exist_ok=True)

    F = modelo.ficha
    md = [f"# {modelo.nombre}", ""]
    if modelo.id:
        md += [f"**Posición curricular:** {modelo.id} (nivel {modelo.nivel}) — "
               f"ver `docs/LABORATORIO_MACRO.md`", ""]

    if F:
        md += ["## Contexto histórico", "", F.contexto, "",
               "## Autores y escuelas", "", F.autores, "",
               "## Supuestos", ""]
        md += [f"- {s}" for s in F.supuestos]
        md += ["", "## Ecuaciones", ""]
        for e in F.ecuaciones:
            md += [f"**{e.nombre}**", "", f"$${e.latex}$$", "", e.significado, ""]
        md += ["## Intuición económica", "", F.intuicion, ""]
        if F.equilibrio:
            md += ["## Equilibrio y estabilidad", "", F.equilibrio, ""]

    # --- parámetros y resultados base ---
    md += ["## Parámetros", "",
           _tabla([(p.nombre, p.etiqueta, base.fmt(p.valor),
                    f"[{base.fmt(p.minimo)}, {base.fmt(p.maximo)}]")
                   for p in modelo.parametros],
                  ("parámetro", "significado", "valor", "rango")), ""]

    res_base = modelo.calcular()
    if res_base:
        md += ["## Resultados con parámetros base", "",
               _tabla([(k, base.fmt(v)) for k, v in res_base.items()],
                      ("magnitud", "valor")), ""]

    fig = base.figura(modelo)
    fig.savefig(carpeta / "fig_base.png", dpi=config.DPI, bbox_inches="tight")
    plt.close(fig)
    md += ["![situación base](fig_base.png)", ""]

    # --- escenarios: experimento, tabla comparativa, figura, lectura ---
    if modelo.escenarios:
        md += ["## Escenarios (experimentos de simulación)", ""]
        for esc in modelo.escenarios:
            cambios = ", ".join(f"{k} → {base.fmt(v)}" for k, v in esc.cambios.items())
            md += [f"### {esc.nombre}", "", f"{esc.descripcion} ({cambios})", ""]
            res_esc = modelo.calcular(**esc.cambios)
            if res_base and res_esc:
                md += [_comparacion(res_base, res_esc), ""]
            fig = base.figura(modelo, dict(modelo.dict_params(), **esc.cambios),
                              titulo=esc.nombre)
            nombre_fig = f"fig_{esc.nombre}.png"
            fig.savefig(carpeta / nombre_fig, dpi=config.DPI, bbox_inches="tight")
            plt.close(fig)
            md += [f"![{esc.nombre}]({nombre_fig})", ""]
            if esc.lectura:
                md += [f"**Lectura económica:** {esc.lectura}", ""]

    # --- limitaciones y evolución (el puente curricular) ---
    if F:
        if F.limitaciones:
            md += ["## Limitaciones y críticas", ""]
            md += [f"- {l}" for l in F.limitaciones] + [""]
        if F.evolucion:
            md += ["## Evolución: hacia el siguiente modelo", "", F.evolucion, ""]

    # --- verificaciones (validación del principio rector) ---
    checks = base.verificar(modelo)
    if checks:
        md += ["## Verificaciones numéricas", "",
               _tabla([("✔" if ok else "✘", nombre, detalle)
                       for nombre, ok, detalle in checks],
                      ("", "verificación", "detalle")), ""]

    if F:
        md += ["---", "", f"**Procedencia:** {F.procedencia}", ""]
        if F.referencias:
            md += ["**Referencias:**", ""] + [f"- {r}" for r in F.referencias] + [""]
    if modelo.notas:
        md += [f"> {modelo.notas}", ""]

    ruta = carpeta / "reporte.md"
    ruta.write_text("\n".join(md), encoding="utf-8")
    return ruta
