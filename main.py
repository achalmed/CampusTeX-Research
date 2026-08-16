#!/usr/bin/env python3
# main.py — simuladores interactivos de teoría económica.
#
#   interactivo <modelo>              ventana con sliders (requiere display)
#   demo <modelo> --param G --valores 100,200,300 [--salida f.pdf]
#                                     headless: efecto comparativo de un parámetro
#   listar                            modelos disponibles
#
# Modelos en simuladores/modelos/ (islm, …); añadir uno = definir un Modelo.

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base

DIR_MODELOS = Path(__file__).resolve().parent / "modelos"


def _cargar(nombre):
    sys.path.insert(0, str(DIR_MODELOS))
    return importlib.import_module(nombre).MODELO


def cmd_interactivo(a):
    base.interactivo(_cargar(a.modelo))
    return 0


def cmd_demo(a):
    modelo = _cargar(a.modelo)
    valores = [float(v) for v in a.valores.split(",")]
    salida = a.salida or f"/tmp/{a.modelo}_{a.param}.pdf"
    ruta = base.demo(modelo, a.param, valores, salida)
    print(f"[✓] demo → {ruta}")
    print(f"    {modelo.nombre}: efecto de {a.param} en {valores}")
    print(f"    {modelo.notas}")
    return 0


def cmd_listar(_a):
    print("Modelos disponibles:")
    for f in sorted(DIR_MODELOS.glob("*.py")):
        if f.stem == "__init__":
            continue
        try:
            m = _cargar(f.stem)
            print(f"  {f.stem:<12} {m.nombre} — {len(m.parametros)} parámetros")
        except Exception as exc:
            print(f"  {f.stem:<12} (error: {exc})")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="datafw-simuladores",
        description="Simuladores interactivos de teoría económica (IS-LM, …).")
    sub = ap.add_subparsers(dest="comando", required=True)
    pi = sub.add_parser("interactivo", help="ventana con sliders")
    pi.add_argument("modelo")
    pd = sub.add_parser("demo", help="render headless de sensibilidad")
    pd.add_argument("modelo"); pd.add_argument("--param", required=True)
    pd.add_argument("--valores", required=True); pd.add_argument("--salida")
    sub.add_parser("listar", help="modelos disponibles")
    a = ap.parse_args()
    sys.exit({"interactivo": cmd_interactivo, "demo": cmd_demo,
              "listar": cmd_listar}[a.comando](a))


if __name__ == "__main__":
    main()
