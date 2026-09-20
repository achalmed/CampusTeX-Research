#!/usr/bin/env python3
"""simuladores/estadistica/main.py — Laboratorio de Estadística Computacional (datafw/simuladores/estadistica).

Disciplina hermana de macro/ bajo el paraguas simuladores/: reusa el MOTOR de
la raíz (base/graficos/reporte/laboratorio) y aporta su propio config + modelos.

USO:
  python3 main.py            ← abre el laboratorio interactivo (o `listar` mientras
                               el app se construye)
  verificar [<modelo>]       control de calidad: los TEOREMAS como chequeos numéricos
  reporte [<modelo>|--todos] informes MD + figuras en salidas/
  listar · ficha · simular · experimento · comparar · sensibilidad · demo

<modelo> acepta id (e02), slug (poblacion_muestra) o archivo (e02_poblacion_muestra).
Currículo: docs/LABORATORIO_ESTADISTICA.md (239 temas, 20 secciones).
"""

import argparse
import importlib
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent          # simuladores/estadistica (config, modelos, app)
sys.path.insert(0, str(_AQUI.parent))            # simuladores/ (MOTOR: base, graficos, reporte, laboratorio)
sys.path.insert(0, str(_AQUI))                   # la disciplina PRIMERO (su config/modelos ganan)
import base
import config
import graficos
import laboratorio as lab
import reporte as reporte_mod


def _es_id(clave):
    """¿'e02', 'm03', 'u01'…? letra(s) + dígitos = id curricular."""
    return len(clave) >= 2 and clave[0].isalpha() and clave[1:].isdigit()


def _descubrir():
    """modelos/**/*.py → {clave: módulo}; clave = archivo, id (e02) y slug."""
    indice = {}
    for f in sorted(config.DIR_MODELOS.rglob("*.py")):
        if f.stem.startswith("_"):
            continue
        rel = f.relative_to(config.DIR_MODELOS).with_suffix("")
        modulo = ".".join(("modelos",) + rel.parts)
        indice[f.stem] = modulo                          # e02_poblacion_muestra
        if "_" in f.stem:
            mid, _, slug = f.stem.partition("_")
            if _es_id(mid):
                indice.setdefault(mid, modulo)           # e02
                indice.setdefault(slug, modulo)          # poblacion_muestra
    return indice


def _cargar(nombre):
    indice = _descubrir()
    if nombre not in indice:
        disponibles = ", ".join(sorted(k for k in indice if _es_id(k))) or "(ninguno todavía)"
        sys.exit(f"[✗] modelo '{nombre}' no encontrado. Implementados: {disponibles}")
    return importlib.import_module(indice[nombre]).MODELO


def _todos():
    vistos, modelos = set(), []
    for modulo in _descubrir().values():
        if modulo in vistos:
            continue
        vistos.add(modulo)
        modelos.append(importlib.import_module(modulo).MODELO)
    return sorted(modelos, key=lambda m: (m.nivel or 99, m.id or m.nombre))


def _tabla_resultados(res):
    ancho = max((len(k) for k in res), default=0)
    for k, v in res.items():
        print(f"    {k.ljust(ancho)}  {base.fmt(v)}")


def cmd_listar(_a):
    modelos = _todos()
    if not modelos:
        print("No hay modelos en modelos/ todavía."); return 0
    print("Temas implementados (currículo: docs/LABORATORIO_ESTADISTICA.md)\n")
    seccion_actual = None
    for m in modelos:
        if m.nivel != seccion_actual:
            seccion_actual = m.nivel
            print(f"  {config.SECCIONES.get(m.nivel, f'Sección {m.nivel}')}")
        extras = []
        if m.escenarios:
            extras.append(f"{len(m.escenarios)} experimentos")
        if m.verificaciones:
            extras.append(f"{len(m.verificaciones)} verificaciones")
        marca = f" — {', '.join(extras)}" if extras else ""
        print(f"    {m.id or '—':<5} {m.nombre}{marca}")
    return 0


def cmd_ficha(a):
    m = _cargar(a.modelo)
    F = m.ficha
    print(f"═══ {m.nombre} ({m.id or 'sin id'}, {config.SECCIONES.get(m.nivel, '—')}) ═══\n")
    if not F:
        print("(modelo sin ficha; solo motor numérico)"); return 0
    if F.pregunta:
        print(f"PREGUNTA\n  {F.pregunta}\n")
    print(f"CONTEXTO HISTÓRICO\n  {F.contexto}\n")
    print(f"AUTORES Y ESCUELAS\n  {F.autores}\n")
    print("SUPUESTOS")
    for s in F.supuestos:
        print(f"  - {s}")
    if F.variables:
        print("\nVARIABLES")
        for simbolo, desc in F.variables:
            print(f"  {simbolo:<12} {desc}")
    print("\nDEFINICIONES / ECUACIONES")
    for e in F.ecuaciones:
        print(f"  [{e.nombre}]  {e.latex}")
        print(f"      {e.significado}")
    if F.derivacion:
        print("\nDERIVACIÓN (paso a paso)")
        for paso in F.derivacion:
            print(f"    {paso}")
    print(f"\nINTUICIÓN\n  {F.intuicion}")
    if F.equilibrio:
        print(f"\nPROPIEDADES\n  {F.equilibrio}")
    if F.limitaciones:
        print("\nLIMITACIONES")
        for l in F.limitaciones:
            print(f"  - {l}")
    if F.evolucion:
        print(f"\nCONEXIÓN CON EL SIGUIENTE TEMA\n  {F.evolucion}")
    if m.escenarios:
        print("\nEXPERIMENTOS (simular/experimento --escenario <nombre>)")
        for e in m.escenarios:
            print(f"  {e.nombre:<22} {e.descripcion}")
    print(f"\nPROCEDENCIA\n  {F.procedencia}")
    return 0


def cmd_simular(a):
    m = _cargar(a.modelo)
    cambios, etiqueta = {}, None
    if a.escenario:
        esc = m.escenario(a.escenario)
        cambios, etiqueta = dict(esc.cambios), esc
    for par in a.param or []:
        k, _, v = par.partition("=")
        cambios[k] = float(v)
    res_base = m.calcular()
    print(f"── {m.nombre} ──")
    if not cambios:
        print("  Resultados (parámetros base):")
        _tabla_resultados(res_base)
    else:
        res_new = m.calcular(**cambios)
        print(f"  Experimento: {etiqueta.descripcion if etiqueta else 'cambio manual'} "
              f"({', '.join(f'{k}→{base.fmt(v)}' for k, v in cambios.items())})")
        ancho = max(len(k) for k in res_base)
        print(f"    {'magnitud'.ljust(ancho)}  {'base':>12}  {'nuevo':>12}  {'Δ':>12}")
        for k, v0 in res_base.items():
            v1 = res_new.get(k)
            if isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
                print(f"    {k.ljust(ancho)}  {base.fmt(v0):>12}  {base.fmt(v1):>12}  "
                      f"{base.fmt(v1 - v0):>12}")
        if etiqueta and etiqueta.cadena:
            print(f"\n  Mecanismo: " + " → ".join(etiqueta.cadena))
        if etiqueta and etiqueta.lectura:
            print(f"\n  ¿Por qué?: {etiqueta.lectura}")
    if m.notas:
        print(f"\n  Nota: {m.notas}")
    return 0


def cmd_comparar(a):
    m = _cargar(a.modelo)
    magnitudes, columnas = base.comparar(m, a.escenarios)
    nombres = list(columnas)
    ancho = max(len(k) for k in magnitudes)
    anchos_col = [max(12, len(n) + 2) for n in nombres]
    print(f"── {m.nombre} — comparación ──\n")
    print("    " + "magnitud".ljust(ancho) + "".join(
        n.rjust(w) for n, w in zip(nombres, anchos_col)))
    for k in magnitudes:
        fila = "    " + k.ljust(ancho)
        for n, w in zip(nombres, anchos_col):
            fila += base.fmt(columnas[n][k]).rjust(w)
        print(fila)
    return 0


def cmd_sensibilidad(a):
    m = _cargar(a.modelo)
    sens = base.sensibilidad(m, a.param, a.magnitud, n=a.puntos)
    print(f"── {m.nombre} — sensibilidad de «{sens['magnitud']}» respecto a {a.param} ──\n")
    for v, y in sens["filas"]:
        marca = "  ← base" if abs(v - sens["base"]) < 1e-9 else ""
        print(f"    {a.param} = {base.fmt(v):>10}   →   {base.fmt(y)}{marca}")
    print(f"\n    ∂({sens['magnitud']})/∂{a.param} = {sens['derivada']:.4f}  (en la base)")
    return 0


def cmd_reporte(a):
    modelos = _todos() if a.todos else [_cargar(a.modelo)]
    for m in modelos:
        ruta = reporte_mod.render(m)
        print(f"[✓] {m.id or m.nombre:<5} → {ruta}")
    return 0


def cmd_verificar(a):
    modelos = [_cargar(a.modelo)] if a.modelo else _todos()
    fallos = total = 0
    for m in modelos:
        for nombre, ok, detalle in base.verificar(m):
            total += 1
            fallos += not ok
            print(f"  {'✔' if ok else '✘'} {m.id or m.nombre:<5} {nombre}: {detalle}")
    print(f"\n{total - fallos}/{total} verificaciones superadas"
          + (f" — {fallos} FALLARON" if fallos else ""))
    return 1 if fallos else 0


def cmd_app(_a=None):
    import app   # simuladores/app.py (motor compartido); config.APP_* y SECCIONES viven en esta disciplina
    app.ejecutar(_todos())
    return 0


def main():
    if len(sys.argv) == 1:
        sys.exit(cmd_app())
    ap = argparse.ArgumentParser(prog="datafw-estadistica",
        description="Laboratorio de Estadística Computacional (disciplina de simuladores/).")
    sub = ap.add_subparsers(dest="comando", required=True)
    sub.add_parser("app", help="abrir el laboratorio interactivo")
    sub.add_parser("listar", help="temas implementados por sección")
    pf = sub.add_parser("ficha", help="ficha pedagógica de un tema")
    pf.add_argument("modelo")
    ps = sub.add_parser("simular", help="resultados / experimento directo")
    ps.add_argument("modelo")
    ps.add_argument("--escenario")
    ps.add_argument("--param", action="append", metavar="k=v")
    pc = sub.add_parser("comparar", help="comparar escenarios")
    pc.add_argument("modelo")
    pc.add_argument("escenarios", nargs="+", metavar="escenario")
    pn = sub.add_parser("sensibilidad", help="∂magnitud/∂parámetro")
    pn.add_argument("modelo")
    pn.add_argument("--param", required=True)
    pn.add_argument("--magnitud")
    pn.add_argument("--puntos", type=int, default=9)
    pr = sub.add_parser("reporte", help="informe MD + figuras en salidas/")
    pr.add_argument("modelo", nargs="?")
    pr.add_argument("--todos", action="store_true")
    pv = sub.add_parser("verificar", help="chequeos numéricos (los teoremas)")
    pv.add_argument("modelo", nargs="?")
    a = ap.parse_args()
    if a.comando == "reporte" and not a.todos and not a.modelo:
        ap.error("reporte requiere <modelo> o --todos")
    sys.exit({"app": cmd_app, "listar": cmd_listar, "ficha": cmd_ficha,
              "simular": cmd_simular, "comparar": cmd_comparar,
              "sensibilidad": cmd_sensibilidad, "reporte": cmd_reporte,
              "verificar": cmd_verificar}[a.comando](a))


if __name__ == "__main__":
    main()
