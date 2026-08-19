#!/usr/bin/env python3
# main.py — laboratorio de macroeconomía computacional (datafw/simuladores).
#
#   listar                                modelos implementados, por nivel del currículo
#   ficha <modelo>                        ficha pedagógica en terminal
#   simular <modelo> [--escenario E] [--param k=v ...]
#                                         resultados de equilibrio; con escenario o
#                                         --param imprime tabla comparativa base vs cambio
#   demo <modelo> --param G --valores 100,200,300 [--salida f.pdf]
#                                         PDF headless: sensibilidad a un parámetro
#   reporte [<modelo>|--todos]            informe MD + figuras en salidas/
#   verificar [<modelo>]                  chequeos numéricos (identidades, convergencias)
#   interactivo <modelo>                  ventana con sliders (requiere display)
#
# <modelo> acepta id curricular (m03), slug (funcion_consumo) o archivo
# (m03_funcion_consumo). Currículo completo: docs/LABORATORIO_MACRO.md.
# Añadir un modelo = un archivo en modelos/nivel_NN/ con ficha + escenarios +
# verificaciones (patrón en modelos/nivel_01/m03_funcion_consumo.py).

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base
import config
import reporte as reporte_mod


def _descubrir():
    """Recorre modelos/**/*.py y devuelve {clave: nombre_de_modulo} admitiendo
    como clave el id (m03), el archivo (m03_funcion_consumo) y el slug
    (funcion_consumo). No importa nada todavía (carga perezosa)."""
    indice = {}
    for f in sorted(config.DIR_MODELOS.rglob("*.py")):
        if f.stem.startswith("_"):
            continue
        rel = f.relative_to(config.DIR_MODELOS).with_suffix("")
        modulo = ".".join(("modelos",) + rel.parts)
        indice[f.stem] = modulo                          # m03_funcion_consumo
        if "_" in f.stem and f.stem.split("_")[0].startswith("m"):
            mid, _, slug = f.stem.partition("_")
            indice.setdefault(mid, modulo)               # m03
            indice.setdefault(slug, modulo)              # funcion_consumo
    return indice


def _cargar(nombre):
    indice = _descubrir()
    if nombre not in indice:
        disponibles = ", ".join(sorted(k for k in indice if k.startswith("m") and k[1:2].isdigit()))
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
    nivel_actual = None
    modelos = _todos()
    if not modelos:
        print("No hay modelos en modelos/."); return 0
    print("Modelos implementados (currículo completo: docs/LABORATORIO_MACRO.md)\n")
    for m in modelos:
        if m.nivel != nivel_actual:
            nivel_actual = m.nivel
            print(f"  Nivel {m.nivel}" if m.nivel else "  (sin nivel)")
        extras = []
        if m.escenarios:
            extras.append(f"{len(m.escenarios)} escenarios")
        if m.verificaciones:
            extras.append(f"{len(m.verificaciones)} verificaciones")
        marca = f" — {', '.join(extras)}" if extras else ""
        print(f"    {m.id or '—':<5} {m.nombre}{marca}")
    return 0


def cmd_ficha(a):
    m = _cargar(a.modelo)
    F = m.ficha
    print(f"═══ {m.nombre} ({m.id or 'sin id'}, nivel {m.nivel or '—'}) ═══\n")
    if not F:
        print("(modelo sin ficha pedagógica; solo motor numérico)"); return 0
    print(f"CONTEXTO HISTÓRICO\n  {F.contexto}\n")
    print(f"AUTORES Y ESCUELAS\n  {F.autores}\n")
    print("SUPUESTOS")
    for s in F.supuestos:
        print(f"  - {s}")
    print("\nECUACIONES")
    for e in F.ecuaciones:
        print(f"  [{e.nombre}]  {e.latex}")
        print(f"      {e.significado}")
    print(f"\nINTUICIÓN\n  {F.intuicion}")
    if F.equilibrio:
        print(f"\nEQUILIBRIO Y ESTABILIDAD\n  {F.equilibrio}")
    if F.limitaciones:
        print("\nLIMITACIONES")
        for l in F.limitaciones:
            print(f"  - {l}")
    if F.evolucion:
        print(f"\nEVOLUCIÓN\n  {F.evolucion}")
    if m.escenarios:
        print("\nESCENARIOS DISPONIBLES (simular --escenario <nombre>)")
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
        if etiqueta and etiqueta.lectura:
            print(f"\n  Lectura económica: {etiqueta.lectura}")
    if m.notas:
        print(f"\n  Nota: {m.notas}")
    return 0


def cmd_demo(a):
    modelo = _cargar(a.modelo)
    valores = [float(v) for v in a.valores.split(",")]
    config.DIR_SALIDAS.mkdir(parents=True, exist_ok=True)
    salida = a.salida or str(config.DIR_SALIDAS / f"demo_{a.modelo}_{a.param}.pdf")
    ruta = base.demo(modelo, a.param, valores, salida)
    print(f"[✓] demo → {ruta}")
    print(f"    {modelo.nombre}: efecto de {a.param} en {valores}")
    if modelo.notas:
        print(f"    {modelo.notas}")
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
        checks = base.verificar(m)
        if not checks:
            print(f"  {m.id or m.nombre:<5} (sin verificaciones)")
            continue
        for nombre, ok, detalle in checks:
            total += 1
            if not ok:
                fallos += 1
            print(f"  {'✔' if ok else '✘'} {m.id or m.nombre:<5} {nombre}: {detalle}")
    print(f"\n{total - fallos}/{total} verificaciones superadas"
          + (f" — {fallos} FALLARON" if fallos else ""))
    return 1 if fallos else 0


def cmd_interactivo(a):
    base.interactivo(_cargar(a.modelo))
    return 0


def main():
    ap = argparse.ArgumentParser(prog="datafw-simuladores",
        description="Laboratorio de macroeconomía computacional: modelos con ficha "
                    "pedagógica, simulación de escenarios y verificación numérica.")
    sub = ap.add_subparsers(dest="comando", required=True)
    sub.add_parser("listar", help="modelos implementados por nivel")
    pf = sub.add_parser("ficha", help="ficha pedagógica de un modelo")
    pf.add_argument("modelo")
    ps = sub.add_parser("simular", help="resultados de equilibrio / experimento")
    ps.add_argument("modelo")
    ps.add_argument("--escenario", help="nombre de un escenario predefinido")
    ps.add_argument("--param", action="append", metavar="k=v",
                    help="cambio manual de parámetro (repetible)")
    pd = sub.add_parser("demo", help="PDF headless de sensibilidad a un parámetro")
    pd.add_argument("modelo"); pd.add_argument("--param", required=True)
    pd.add_argument("--valores", required=True); pd.add_argument("--salida")
    pr = sub.add_parser("reporte", help="informe MD + figuras en salidas/")
    pr.add_argument("modelo", nargs="?")
    pr.add_argument("--todos", action="store_true")
    pv = sub.add_parser("verificar", help="chequeos numéricos de los modelos")
    pv.add_argument("modelo", nargs="?")
    pi = sub.add_parser("interactivo", help="ventana con sliders")
    pi.add_argument("modelo")
    a = ap.parse_args()
    if a.comando == "reporte" and not a.todos and not a.modelo:
        ap.error("reporte requiere <modelo> o --todos")
    sys.exit({"listar": cmd_listar, "ficha": cmd_ficha, "simular": cmd_simular,
              "demo": cmd_demo, "reporte": cmd_reporte, "verificar": cmd_verificar,
              "interactivo": cmd_interactivo}[a.comando](a))


if __name__ == "__main__":
    main()
