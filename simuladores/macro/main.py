#!/usr/bin/env python3
"""simuladores/macro/main.py — Laboratorio de Economía Computacional (datafw/simuladores).

USO NORMAL (la aplicación única):

  python3 main.py            ← abre el Laboratorio Interactivo de Economía

  Todo vive dentro: elegir modelo, recorrido pedagógico progresivo
  (pregunta → construcción → equilibrio → experimentos → interpretación),
  experimentación libre con actualización en vivo, comparaciones y láminas.

HERRAMIENTAS TÉCNICAS (automatización/desarrollo; el usuario final no las
necesita):
  verificar [<modelo>]     control de calidad: chequeos numéricos (100% exigido)
  reporte [<modelo>|--todos]  regenera informes MD + láminas en salidas/
  listar · ficha · simular · experimento · comparar · sensibilidad · demo ·
  laboratorio · interactivo   equivalentes por terminal de lo que la app
                              hace por dentro (útiles para scripts y CI)

<modelo> acepta id curricular (m03), slug (funcion_consumo) o archivo
(m03_funcion_consumo). Currículo completo: docs/laboratorio-macro.md.
"""

import argparse
import importlib
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent          # simuladores/macro (config, modelos, app)
sys.path.insert(0, str(_AQUI.parent))            # simuladores/ (MOTOR: base, graficos, reporte, laboratorio)
sys.path.insert(0, str(_AQUI))                   # la disciplina PRIMERO (su config/modelos ganan)
import base
import config
import graficos
import laboratorio as lab
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
    print("Modelos implementados (currículo completo: docs/laboratorio-macro.md)\n")
    for m in modelos:
        if m.nivel != nivel_actual:
            nivel_actual = m.nivel
            print(f"  Nivel {m.nivel}" if m.nivel else "  (sin nivel)")
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
    print(f"═══ {m.nombre} ({m.id or 'sin id'}, nivel {m.nivel or '—'}) ═══\n")
    if not F:
        print("(modelo sin ficha pedagógica; solo motor numérico)"); return 0
    if F.pregunta:
        print(f"PREGUNTA ECONÓMICA\n  {F.pregunta}\n")
    print(f"CONTEXTO HISTÓRICO\n  {F.contexto}\n")
    print(f"AUTORES Y ESCUELAS\n  {F.autores}\n")
    print("SUPUESTOS")
    for s in F.supuestos:
        print(f"  - {s}")
    if F.variables:
        print("\nVARIABLES")
        for simbolo, desc in F.variables:
            print(f"  {simbolo:<10} {desc}")
    print("\nECUACIONES")
    for e in F.ecuaciones:
        print(f"  [{e.nombre}]  {e.latex}")
        print(f"      {e.significado}")
    if F.derivacion:
        print("\nDERIVACIÓN DEL EQUILIBRIO")
        for paso in F.derivacion:
            print(f"    {paso}")
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
        print("\nEXPERIMENTOS DISPONIBLES (experimento/simular --escenario <nombre>)")
        for e in m.escenarios:
            print(f"  {e.nombre:<22} {e.descripcion}")
    print(f"\nPROCEDENCIA\n  {F.procedencia}")
    return 0


def _leer_prediccion(pregunta):
    equivalencias = {"↑": "↑", "u": "↑", "s": "↑", "+": "↑", "sube": "↑",
                     "↓": "↓", "d": "↓", "b": "↓", "-": "↓", "baja": "↓",
                     "=": "=", "0": "=", "igual": "="}
    while True:
        r = input(f"    {pregunta}  [↑/↓/=] → ").strip().lower()
        if r in equivalencias:
            return equivalencias[r]
        print("      (responde ↑, ↓ o = — también valen s/b/= )")


def cmd_experimento(a):
    """El corazón pedagógico: hipótesis → ejecutar → verificar → mecanismo."""
    m = _cargar(a.modelo)
    if not m.escenarios:
        sys.exit(f"[✗] {m.id} no tiene experimentos declarados")
    esc = m.escenario(a.escenario) if a.escenario else None
    print(f"═══ LABORATORIO · {m.nombre} ({m.id}) ═══\n")
    if m.ficha and m.ficha.pregunta:
        print(f"  Pregunta del modelo: {m.ficha.pregunta}\n")
    if esc is None:
        print("  Experimentos disponibles:")
        for i, e in enumerate(m.escenarios, 1):
            print(f"    {i}. {e.nombre:<22} {e.descripcion}")
        idx = input("\n  Elige un experimento [número] → ").strip()
        try:
            esc = m.escenarios[int(idx) - 1]
        except (ValueError, IndexError):
            sys.exit("[✗] selección inválida")
    cambios = ", ".join(f"{k}: {base.fmt(m.parametro(k).valor)} → {base.fmt(v)}"
                        for k, v in esc.cambios.items())
    print(f"\n  🧪 Experimento: {esc.descripcion}")
    print(f"     Cambio: {cambios}")
    if m.ficha and m.ficha.supuestos:
        print(f"     Recuerda el supuesto clave: {m.ficha.supuestos[0]}")

    res0 = m.calcular()
    res1 = m.calcular(**esc.cambios)
    claves = [k for k in res0
              if isinstance(res0[k], (int, float)) and isinstance(res1.get(k), (int, float))][:4]

    print("\n  Antes de ejecutar — TU HIPÓTESIS: ¿qué pasará con…?")
    predicciones = {k: _leer_prediccion(k) for k in claves}

    print("\n  ▶ EJECUTANDO EXPERIMENTO…\n")
    aciertos = 0
    ancho = max(len(k) for k in claves)
    print(f"    {'magnitud'.ljust(ancho)}  {'tu hipótesis':>12}  {'resultado':>10}  ")
    for k in claves:
        real = base.signo(res1[k] - res0[k])
        ok = predicciones[k] == real
        aciertos += ok
        print(f"    {k.ljust(ancho)}  {predicciones[k]:>12}  {real:>9}  {'✔' if ok else '✘'}")
    print(f"\n  Puntaje: {aciertos}/{len(claves)}")

    print(f"\n  RESULTADOS")
    for k in claves:
        print(f"    {k.ljust(ancho)}  {base.fmt(res0[k]):>10} → {base.fmt(res1[k]):>10}  "
              f"(Δ {base.fmt(res1[k] - res0[k])})")
    if esc.cadena:
        print(f"\n  MECANISMO DE TRANSMISIÓN\n    " + "  →  ".join(esc.cadena))
    if esc.lectura:
        print(f"\n  ¿POR QUÉ?\n    {esc.lectura}")
    if m.ficha and m.ficha.evolucion:
        print(f"\n  PARA SEGUIR: {m.ficha.evolucion.split('.')[0]}.")
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
    print(f"── {m.nombre} — comparación de políticas ──\n")
    print("    " + "magnitud".ljust(ancho) + "".join(
        n.rjust(w) for n, w in zip(nombres, anchos_col)))
    for k in magnitudes:
        fila = "    " + k.ljust(ancho)
        for n, w in zip(nombres, anchos_col):
            fila += base.fmt(columnas[n][k]).rjust(w)
        print(fila)
    print("\n  (columna 'base' = parámetros por defecto; cada escenario aplica sus cambios)")
    return 0


def cmd_sensibilidad(a):
    m = _cargar(a.modelo)
    sens = base.sensibilidad(m, a.param, a.magnitud, n=a.puntos)
    print(f"── {m.nombre} — sensibilidad de «{sens['magnitud']}» respecto a {a.param} ──\n")
    for v, y in sens["filas"]:
        marca = "  ← base" if abs(v - sens["base"]) < 1e-9 else ""
        print(f"    {a.param} = {base.fmt(v):>10}   →   {base.fmt(y)}{marca}")
    print(f"\n    ∂({sens['magnitud']})/∂{a.param} = {sens['derivada']:.4f}  (en la base)")
    if a.grafico:
        config.DIR_SALIDAS.mkdir(parents=True, exist_ok=True)
        ruta = config.DIR_SALIDAS / f"sensibilidad_{m.id}_{a.param}.png"
        fig = graficos.figura_sensibilidad(m, sens)
        fig.savefig(ruta, dpi=config.DPI)
        print(f"\n[✓] gráfico → {ruta}")
    return 0


def cmd_demo(a):
    modelo = _cargar(a.modelo)
    valores = [float(v) for v in a.valores.split(",")]
    config.DIR_SALIDAS.mkdir(parents=True, exist_ok=True)
    salida = a.salida or str(config.DIR_SALIDAS / f"demo_{a.modelo}_{a.param}.pdf")
    ruta = graficos.demo(modelo, a.param, valores, salida)
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


def cmd_laboratorio(a):
    lab.laboratorio(_cargar(a.modelo))
    return 0


def cmd_interactivo(a):
    lab.interactivo(_cargar(a.modelo))
    return 0


def cmd_app(_a=None):
    import app
    app.ejecutar(_todos())
    return 0


def main():
    if len(sys.argv) == 1:              # sin argumentos → la aplicación única
        sys.exit(cmd_app())
    ap = argparse.ArgumentParser(prog="datafw-simuladores",
        description="Laboratorio de Economía Computacional. Sin argumentos abre "
                    "la aplicación única; los subcomandos son herramientas "
                    "técnicas para automatización.")
    sub = ap.add_subparsers(dest="comando", required=True)
    sub.add_parser("app", help="abrir el Laboratorio Interactivo (= sin argumentos)")
    sub.add_parser("listar", help="modelos implementados por nivel")
    pf = sub.add_parser("ficha", help="ficha pedagógica de un modelo")
    pf.add_argument("modelo")
    pe = sub.add_parser("experimento", help="modo laboratorio: hipótesis → ejecutar → verificar")
    pe.add_argument("modelo")
    pe.add_argument("--escenario", help="experimento concreto (si no, menú)")
    ps = sub.add_parser("simular", help="resultados de equilibrio / experimento directo")
    ps.add_argument("modelo")
    ps.add_argument("--escenario", help="nombre de un escenario predefinido")
    ps.add_argument("--param", action="append", metavar="k=v",
                    help="cambio manual de parámetro (repetible)")
    pc = sub.add_parser("comparar", help="comparación de políticas (varios escenarios)")
    pc.add_argument("modelo")
    pc.add_argument("escenarios", nargs="+", metavar="escenario")
    pn = sub.add_parser("sensibilidad", help="∂magnitud/∂parámetro + tabla en malla")
    pn.add_argument("modelo")
    pn.add_argument("--param", required=True)
    pn.add_argument("--magnitud", help="clave de resultados() (default: la primera)")
    pn.add_argument("--puntos", type=int, default=9)
    pn.add_argument("--grafico", action="store_true", help="guardar PNG en salidas/")
    pd = sub.add_parser("demo", help="PDF headless de sensibilidad a un parámetro")
    pd.add_argument("modelo"); pd.add_argument("--param", required=True)
    pd.add_argument("--valores", required=True); pd.add_argument("--salida")
    pr = sub.add_parser("reporte", help="informe MD + láminas en salidas/")
    pr.add_argument("modelo", nargs="?")
    pr.add_argument("--todos", action="store_true")
    pv = sub.add_parser("verificar", help="chequeos numéricos de los modelos")
    pv.add_argument("modelo", nargs="?")
    pl = sub.add_parser("laboratorio", help="ventana con selector de experimentos")
    pl.add_argument("modelo")
    pi = sub.add_parser("interactivo", help="modo avanzado: sliders libres")
    pi.add_argument("modelo")
    a = ap.parse_args()
    if a.comando == "reporte" and not a.todos and not a.modelo:
        ap.error("reporte requiere <modelo> o --todos")
    sys.exit({"app": cmd_app, "listar": cmd_listar, "ficha": cmd_ficha,
              "experimento": cmd_experimento, "simular": cmd_simular,
              "comparar": cmd_comparar, "sensibilidad": cmd_sensibilidad,
              "demo": cmd_demo, "reporte": cmd_reporte, "verificar": cmd_verificar,
              "laboratorio": cmd_laboratorio,
              "interactivo": cmd_interactivo}[a.comando](a))


if __name__ == "__main__":
    main()
