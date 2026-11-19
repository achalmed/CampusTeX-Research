#!/usr/bin/env python3
"""alineamiento.py — matriz de alineamiento, rúbricas, banco de recuperación y política de IA de un curso.

Uso:
  python3 scripts/alineamiento.py verificar [CURSO…]           # sin argumentos, todos los cursos
  python3 scripts/alineamiento.py matriz CURSO [--formato md|tex]
  python3 scripts/alineamiento.py rubrica RUBRICA.yml [--formato md|tex]
  python3 scripts/alineamiento.py calificar RUBRICA.yml PUNTAJES.csv   # columnas: codigo,<clave>,<clave>…
  python3 scripts/alineamiento.py banco CURSO SESION [--examen] [--semilla N] [--formato md|tex] [--estudiante]
  python3 scripts/alineamiento.py pre-post CURSO [--formato md|tex] [--estudiante]
  python3 scripts/alineamiento.py generar CURSO [--aplicar]       # vistas .tex; sin --aplicar solo simula

--estudiante: la versión que se publica, sin claves. `calificar` da la nota vigesimal (nota_100 × 20 / 100) y la
ponderada sobre 100 del formato común de rúbricas, con sus vetos.

CURSO es el slug (contenido/cursos/<slug>) o la ruta; SESION, `sNN` o el nombre de la carpeta.
Salida: 0 bien · 1 algún error ([XX]; los avisos [!!] no hacen fallar) · 2 error de uso.

Qué verifica (docs/estandar-docencia.md §10; norma FLUJO_DE_CONOCIMIENTO, campos 10, 11 y 12):
  - Alineamiento constructivo: todo resultado con su evidencia (evaluación) y su actividad (sesión); toda
    evaluación con al menos un resultado declarado. Biggs (1996); Wiggins y McTighe (2005).
  - Rúbricas analíticas: todo YAML de 01-diseno/rubricas/ cumple el formato común del ecosistema
    (escritura/config/entrega/rubrica.schema.yml, validado por escritura/scripts/entrega/rubrica.py), con los pesos
    sumando 100; el resultado que mide cada criterio va en curso.yml → alineamiento.rubricas.
    Jonsson y Svingby (2007); Panadero y Jonsson (2013).
  - Banco de recuperación por sesión: preguntas ligadas a un resultado; el cuestionario de cada clase intercala
    sesiones anteriores espaciadas. Roediger y Karpicke (2006); Cepeda et al. (2006).
  - Política de IA por evaluación, de un vocabulario cerrado. Comisión Europea (2025); CONCYTEC (2024).
  - Sesión de aprendizaje activo: problema, trabajo en parejas y puesta en común. Freeman et al. (2014);
    Allgood et al. (2015).
  - Evaluación del propio curso: dos o tres resultados clave con preguntas antes y después. Black y Wiliam
    (1998); Allgood et al. (2015).
Un curso sin `alineamiento:` solo pasa por la verificación de sus sesiones de aprendizaje activo.
"""
from __future__ import annotations

import csv
import os
import random
import re
import sys
from pathlib import Path

import yaml

FRAMEWORK = Path(__file__).resolve().parents[1]
CURSOS = FRAMEWORK / "contenido" / "cursos"

# core/env.py: la raíz del workspace y la carpeta de escritura (WRITING_DIR), dueña del formato común de rúbricas.
_d = FRAMEWORK
while _d != _d.parent and not (_d / "core" / "env.py").is_file():
    _d = _d.parent
if (_d / "core" / "env.py").is_file():
    sys.path.insert(0, str(_d / "core"))
    import env  # noqa: E402
    ESCRITURA = Path(env.WRITING_DIR)
else:
    ESCRITURA = Path(os.environ.get("WRITING_DIR", FRAMEWORK.parent / "escritura"))
VALIDADOR_RUBRICA = ESCRITURA / "scripts" / "entrega" / "rubrica.py"   # lee config/entrega/rubrica.schema.yml
NOTA_VIGESIMAL = 20.0   # el esquema califica sobre 100; el registro del curso, sobre 20 (nota_100 × 20 / 100)

FUENTE = {
    "alineamiento": "Biggs (1996); Wiggins y McTighe (2005)",
    "rubrica": "Jonsson y Svingby (2007); Panadero y Jonsson (2013)",
    "banco": "Roediger y Karpicke (2006); Cepeda et al. (2006)",
    "ia": "Comisión Europea (2025); CONCYTEC (2024)",
    "activo": "Freeman et al. (2014); Allgood et al. (2015)",
    "curso": "Black y Wiliam (1998); Allgood et al. (2015)",
}

# Taxonomía SOLO (Biggs): el nivel de comprensión que pide el verbo del resultado.
NIVELES_SOLO = ("uniestructural", "multiestructural", "relacional", "abstracto_ampliado")
TIPOS_EVALUACION = ("formativa", "sumativa")
TIPOS_PREGUNTA = ("abierta", "opcion", "numerica")
# Vocabulario cerrado de uso de IA por evaluación (decisión de diseño 2026-11-18, docs/decisiones.md): del uso
# nulo al libre, siempre declarado y verificado por quien entrega, que responde por todo el contenido.
POLITICA_IA = {
    "prohibida": "Sin herramientas de IA generativa.",
    "apoyo": "IA solo para ideas, dudas y revisión de lenguaje; se declara.",
    "asistida": "IA para código o borrador, verificado línea a línea; se declara cada uso.",
    "libre": "Cualquier uso, declarado y verificado; quien entrega responde por todo.",
}
DINAMICAS = {"aprendizaje_activo": ("Problema", "Trabajo en parejas", "Puesta en común")}
# Distancias del repaso espaciado e intercalado: cuántas sesiones atrás se vuelve a preguntar (decisión de diseño;
# el beneficio del espaciado es de Cepeda et al., 2006; las distancias exactas no salen de la obra).
DISTANCIAS_REPASO = ((1, 2), (2, 1), (4, 1), (8, 1))
MARCA_GENERADO = "% GENERADO por scripts/alineamiento.py generar; no editar."


class Informe:
    """Acumula errores y avisos con su porqué y su fuente."""

    def __init__(self, curso: str):
        self.curso, self.errores, self.avisos = curso, [], []

    def error(self, msg: str, fuente: str):
        self.errores.append(f"[XX] {self.curso}: {msg} · {FUENTE[fuente]}")

    def aviso(self, msg: str, fuente: str):
        self.avisos.append(f"[!!] {self.curso}: {msg} · {FUENTE[fuente]}")


# ---------------------------------------------------------------------------------------------------- lectura

def leer(ruta: Path) -> dict:
    return yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}


def curso_dir(arg: str) -> Path:
    p = Path(arg)
    if (p / "curso.yml").is_file():
        return p.resolve()
    if (CURSOS / arg / "curso.yml").is_file():
        return CURSOS / arg
    raise SystemExit(f"No es un curso: {arg}")


def sesiones(curso: Path) -> list[Path]:
    return sorted(p for p in (curso / "03-sesiones").glob("s[0-9][0-9]-*") if (p / "sesion.yml").is_file())


def sesion_dir(curso: Path, arg: str) -> Path:
    for s in sesiones(curso):
        if s.name == arg or s.name.startswith(arg + "-") or s.name[1:3] == arg.lstrip("s").zfill(2):
            return s
    raise SystemExit(f"No hay sesión «{arg}» en {curso.name}")


def banco_de(sesion: Path) -> dict | None:
    r = sesion / "recuperacion.yml"
    return leer(r) if r.is_file() else None


# ---------------------------------------------------------------------------------------------------- rúbricas

_FORMATO = None


def formato_comun():
    """El módulo de escritura que valida el formato común de rúbricas (None si escritura no está)."""
    global _FORMATO
    if _FORMATO is None and VALIDADOR_RUBRICA.is_file():
        import importlib.util
        spec = importlib.util.spec_from_file_location("rubrica_escritura", VALIDADOR_RUBRICA)
        _FORMATO = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_FORMATO)
    return _FORMATO


def problemas_rubrica(rub: dict) -> list[str]:
    """Errores de una rúbrica: el esquema común de escritura (rubrica.schema.yml) más la regla del curso (pesos = 100).

    Sin escritura en el disco, solo la regla del curso y un error que lo dice: una rúbrica que no pasó por el esquema
    no se da por buena.
    """
    if not isinstance(rub, dict):
        return ["no es un mapa YAML"]
    fc = formato_comun()
    out = list(fc.validar(rub)) if fc else [f"no se encuentra el validador del formato común ({VALIDADOR_RUBRICA})"]
    crit = [c for c in rub.get("criterios") or [] if isinstance(c, dict)]
    try:
        total = sum(float(c.get("peso", 0)) for c in crit)
    except (TypeError, ValueError):
        total = -1
    if crit and abs(total - 100) > 1e-6:
        out.append(f"los pesos suman {total:g}, no 100 (regla del curso: la nota se lee como porcentaje)")
    return out


def escala(rub: dict) -> list[tuple[float, str]]:
    """Los puntajes de la rúbrica (de mayor a menor) con el nombre del nivel (`nombre` del esquema), si lo declara."""
    nombres: dict[float, str] = {}
    for c in rub.get("criterios") or []:
        for n in c.get("niveles") or []:
            if n.get("nombre"):
                nombres.setdefault(n["puntaje"], n["nombre"])
    pts = sorted({n["puntaje"] for c in rub.get("criterios") or [] for n in c.get("niveles") or []}, reverse=True)
    return [(p, nombres.get(p, "")) for p in pts]


def calificar(rub: dict, puntajes: dict[str, float], nota_max: float = NOTA_VIGESIMAL) -> dict:
    """{nota (de 0 a nota_max), nota_100, vetos}: la ponderada del esquema común (`nota` de escritura) llevada a nota_max.

    Cada puntaje ha de ser uno de los niveles de su criterio.
    """
    leidos = {}
    for c in rub["criterios"]:
        p = float(puntajes[c["clave"]])
        if p not in {float(n["puntaje"]) for n in c["niveles"]}:
            raise ValueError(f"puntaje {p:g} fuera de los niveles de «{c['clave']}»")
        leidos[c["clave"]] = p
    fc = formato_comun()
    if fc is None:
        raise SystemExit(f"No se encuentra el validador del formato común de rúbricas: {VALIDADOR_RUBRICA}")
    r = fc.nota(rub, leidos)   # la ponderada sobre 100 (redondeada a un decimal) y los vetos, del formato común
    # la vigesimal, con la misma fórmula sin el redondeo intermedio (68,75 / 100 × 20 = 13,75, no 13,76)
    exacta = sum(leidos[c["clave"]] / fc.maximo(c) * c["peso"] for c in rub["criterios"]) / sum(c["peso"] for c in rub["criterios"])
    return {"nota": round(exacta * nota_max, 2), "nota_100": r["nota"], "vetos": r["vetos"]}


def rubricas_del_curso(curso: Path) -> list[Path]:
    """Todos los YAML de `01-diseno/rubricas/` (los use o no una evaluación: todos han de cumplir el esquema)."""
    return sorted((curso / "01-diseno" / "rubricas").glob("*.yml"))


# ---------------------------------------------------------------------------------------------------- verificación

def verificar_sesiones(curso: Path, inf: Informe, ids_res: set[str] | None):
    """Dinámica activa (en todos los cursos) y, si el curso está alineado, resultados y banco por sesión."""
    preguntas_vistas: dict[str, str] = {}
    for s in sesiones(curso):
        sy = leer(s / "sesion.yml")
        din = sy.get("dinamica")
        if din:
            if din not in DINAMICAS:
                inf.error(f"{s.name}: dinámica «{din}» fuera de {sorted(DINAMICAS)}", "activo")
            else:
                guion = (s / "guion.md").read_text(encoding="utf-8") if (s / "guion.md").is_file() else ""
                titulos = re.findall(r"^##\s+(.+?)\s*$", guion, flags=re.M)
                for fase in DINAMICAS[din]:
                    t = next((x for x in titulos if x.lower().startswith(fase.lower())), None)
                    if t is None:
                        inf.error(f"{s.name}: el guion de aprendizaje activo no tiene «## {fase}»", "activo")
                    elif not re.search(r"\(\s*\d+\s*min\s*\)", t):
                        inf.aviso(f"{s.name}: «## {fase}» sin su tiempo «(NN min)»", "activo")
        if ids_res is None:
            continue
        ra = [x for x in (sy.get("resultados_aprendizaje") or []) if isinstance(x, str)]
        for x in ra:
            if x not in ids_res:
                inf.error(f"{s.name}: resultado «{x}» no declarado en curso.yml", "alineamiento")
        if not ra:
            inf.aviso(f"{s.name}: sesión sin `resultados_aprendizaje` (no cuenta como actividad)", "alineamiento")
            continue
        banco = banco_de(s)
        if banco is None:
            inf.error(f"{s.name}: falta recuperacion.yml (banco de recuperación de la sesión)", "banco")
            continue
        if not banco.get("fuente"):
            inf.error(f"{s.name}: recuperacion.yml sin `fuente`", "banco")
        pregs = banco.get("preguntas") or []
        if len(pregs) < 3:
            inf.error(f"{s.name}: banco con {len(pregs)} preguntas (mínimo 3)", "banco")
        cubiertos = set()
        for p in pregs:
            pid = p.get("id")
            if not pid:
                inf.error(f"{s.name}: pregunta sin `id`", "banco")
                continue
            if pid in preguntas_vistas:
                inf.error(f"{s.name}: id de pregunta repetido «{pid}» (ya en {preguntas_vistas[pid]})", "banco")
            preguntas_vistas[pid] = s.name
            if p.get("resultado") not in ids_res:
                inf.error(f"{s.name}/{pid}: resultado «{p.get('resultado')}» no declarado", "banco")
            cubiertos.add(p.get("resultado"))
            if p.get("tipo") not in TIPOS_PREGUNTA:
                inf.error(f"{s.name}/{pid}: tipo «{p.get('tipo')}» fuera de {list(TIPOS_PREGUNTA)}", "banco")
            if not str(p.get("enunciado") or "").strip() or p.get("respuesta") in (None, ""):
                inf.error(f"{s.name}/{pid}: sin enunciado o sin respuesta", "banco")
            if p.get("tipo") == "opcion" and p.get("respuesta") not in (p.get("opciones") or []):
                inf.error(f"{s.name}/{pid}: la respuesta no está entre las opciones", "banco")
        for x in ra:
            if x not in cubiertos:
                inf.aviso(f"{s.name}: ninguna pregunta del banco recupera «{x}»", "banco")


def verificar_curso(curso: Path) -> Informe:
    inf = Informe(curso.name)
    cy = leer(curso / "curso.yml")
    al = cy.get("alineamiento")
    # toda rúbrica del curso cumple el formato común (escritura/config/entrega/rubrica.schema.yml), la use o no
    # una evaluación: así LaTeX Studio la puede leer para la autoevaluación
    rubricas: dict[str, dict] = {}
    for ruta in rubricas_del_curso(curso):
        try:
            rub = leer(ruta)
        except yaml.YAMLError as ex:
            inf.error(f"rúbrica {ruta.name}: YAML ilegible ({ex})", "rubrica")
            continue
        for p in problemas_rubrica(rub):
            inf.error(f"rúbrica {ruta.name}: {p}", "rubrica")
        if isinstance(rub, dict):
            rubricas[ruta.relative_to(curso).as_posix()] = rub
    if not al:
        verificar_sesiones(curso, inf, None)
        return inf
    res = al.get("resultados") or []
    evs = al.get("evaluaciones") or []
    ids_res = {r.get("id") for r in res}
    if not res:
        inf.error("`alineamiento` sin resultados", "alineamiento")
    for r in res:
        if not r.get("id") or not str(r.get("enunciado") or "").strip():
            inf.error("resultado sin `id` o sin `enunciado`", "alineamiento")
        if r.get("nivel") and r["nivel"] not in NIVELES_SOLO:
            inf.error(f"{r.get('id')}: nivel «{r['nivel']}» fuera de la taxonomía SOLO {list(NIVELES_SOLO)}", "alineamiento")
    nombres_sesion = {s.name for s in sesiones(curso)}
    ids_ev = set()
    peso_sumativo = 0.0
    if not (cy.get("politica_ia") or {}).get("regla"):
        inf.error("curso.yml sin `politica_ia.regla` (política de IA del curso)", "ia")
    for e in evs:
        eid = e.get("id")
        if not eid or eid in ids_ev:
            inf.error(f"evaluación sin `id` o repetida: {eid}", "alineamiento")
        ids_ev.add(eid)
        rs = e.get("resultados") or []
        if not rs:
            inf.error(f"evaluación «{eid}» sin resultado de aprendizaje", "alineamiento")
        for x in rs:
            if x not in ids_res:
                inf.error(f"evaluación «{eid}» apunta a un resultado inexistente «{x}»", "alineamiento")
        if e.get("tipo") not in TIPOS_EVALUACION:
            inf.error(f"evaluación «{eid}»: tipo «{e.get('tipo')}» fuera de {list(TIPOS_EVALUACION)}", "alineamiento")
        if e.get("tipo") == "sumativa":
            try:
                peso_sumativo += float(e.get("peso") or 0)
            except (TypeError, ValueError):
                inf.error(f"evaluación «{eid}»: peso no numérico", "alineamiento")
        if e.get("politica_ia") not in POLITICA_IA:
            inf.error(f"evaluación «{eid}»: `politica_ia` «{e.get('politica_ia')}» fuera de {list(POLITICA_IA)}", "ia")
        if e.get("sesion") and e["sesion"] not in nombres_sesion:
            inf.error(f"evaluación «{eid}»: sesión «{e['sesion']}» inexistente", "alineamiento")
        if e.get("consigna") and not (curso / e["consigna"]).is_file():
            inf.error(f"evaluación «{eid}»: consigna «{e['consigna']}» inexistente", "rubrica")
        if e.get("rubrica"):
            rub = rubricas.get(Path(e["rubrica"]).as_posix())
            if rub is None:
                inf.error(f"evaluación «{eid}»: rúbrica «{e['rubrica']}» inexistente (o fuera de 01-diseno/rubricas/)",
                          "rubrica")
            else:
                mide = (al.get("rubricas") or {}).get(rub.get("clave") or Path(e["rubrica"]).stem) or {}
                for c in rub.get("criterios") or []:
                    x = mide.get(c.get("clave"))
                    if x and x not in rs:
                        inf.error(f"rúbrica {Path(e['rubrica']).name}: el criterio «{c.get('clave')}» mide «{x}», "
                                  f"que la evaluación «{eid}» no declara", "alineamiento")
        elif e.get("tipo") == "sumativa" and e.get("instrumento") != "prueba":
            inf.aviso(f"evaluación sumativa «{eid}» sin rúbrica (o `instrumento: prueba`)", "rubrica")
    if evs and abs(peso_sumativo - 100) > 1e-6:
        inf.error(f"los pesos de las evaluaciones sumativas suman {peso_sumativo:g}, no 100", "alineamiento")
    # criterio → resultado (alineamiento.rubricas: el formato común de rúbricas no guarda el resultado)
    por_clave = {(r.get("clave") or Path(k).stem): r for k, r in rubricas.items()}
    usadas = {(por_clave.get(Path(e["rubrica"]).stem) or {}).get("clave") or Path(e["rubrica"]).stem
              for e in evs if e.get("rubrica")}
    mapa = al.get("rubricas") or {}
    for clave_rub, mide in mapa.items():
        rub = por_clave.get(clave_rub)
        if rub is None:
            inf.error(f"alineamiento.rubricas: «{clave_rub}» no es la clave de ninguna rúbrica de 01-diseno/rubricas/",
                      "alineamiento")
            continue
        criterios = {c.get("clave") for c in rub.get("criterios") or []}
        for c, x in (mide or {}).items():
            if c not in criterios:
                inf.error(f"alineamiento.rubricas.{clave_rub}: criterio «{c}» inexistente en la rúbrica", "alineamiento")
            if x not in ids_res:
                inf.error(f"alineamiento.rubricas.{clave_rub}.{c}: resultado «{x}» no declarado", "alineamiento")
    for clave_rub in sorted(usadas):
        rub = por_clave.get(clave_rub) or {}
        sin = [c.get("clave") for c in rub.get("criterios") or [] if c.get("clave") not in (mapa.get(clave_rub) or {})]
        if sin:
            inf.aviso(f"rúbrica «{clave_rub}»: criterios sin resultado en alineamiento.rubricas: {', '.join(sin)}",
                      "alineamiento")
    # resultado → evidencia → actividad
    actividad: dict[str, list[str]] = {x: [] for x in ids_res}
    for s in sesiones(curso):
        for x in leer(s / "sesion.yml").get("resultados_aprendizaje") or []:
            if x in actividad:
                actividad[x].append(s.name)
    for r in res:
        rid = r.get("id")
        evid = [e for e in evs if rid in (e.get("resultados") or [])]
        if not evid:
            inf.error(f"resultado «{rid}» sin evaluación que lo evidencie", "alineamiento")
        elif all(e.get("tipo") != "sumativa" for e in evid):
            inf.aviso(f"resultado «{rid}» solo con evaluación formativa", "alineamiento")
        if not actividad.get(rid):
            inf.error(f"resultado «{rid}» sin sesión que lo trabaje", "alineamiento")
    verificar_sesiones(curso, inf, ids_res)
    # evaluación del propio curso (C10.6)
    ec = al.get("evaluacion_curso")
    if ec:
        clave = ec.get("resultados") or []
        if not 2 <= len(clave) <= 3:
            inf.error(f"evaluacion_curso con {len(clave)} resultados clave (dos o tres)", "curso")
        conteo = {x: 0 for x in clave}
        for s in sesiones(curso):
            for p in (banco_de(s) or {}).get("preguntas") or []:
                if p.get("resultado") in conteo:
                    conteo[p["resultado"]] += 1
        for x, n in conteo.items():
            if x not in ids_res:
                inf.error(f"evaluacion_curso: resultado «{x}» inexistente", "curso")
            elif n < 2:
                inf.error(f"evaluacion_curso: «{x}» tiene {n} preguntas en los bancos (mínimo 2)", "curso")
    else:
        inf.aviso("sin `alineamiento.evaluacion_curso` (medición antes y después)", "curso")
    # vistas generadas al día
    for ruta, texto in vistas(curso).items():
        if not ruta.is_file():
            inf.error(f"falta la vista {ruta.relative_to(curso)}: corre `alineamiento.py generar {curso.name} --aplicar`",
                      "alineamiento")
        elif ruta.read_text(encoding="utf-8") != texto:
            inf.error(f"vista desfasada {ruta.relative_to(curso)}: corre `alineamiento.py generar {curso.name} --aplicar`",
                      "alineamiento")
    return inf


# ---------------------------------------------------------------------------------------------------- vistas

def tex(s) -> str:
    """Escapa un texto plano para LaTeX (los decimales con coma no se tocan)."""
    s = str(s if s is not None else "")
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")):
        s = s.replace(a, b)
    return s


def num(x) -> str:
    return f"{x:g}".replace(".", ",")


def filas_matriz(curso: Path) -> list[dict]:
    cy = leer(curso / "curso.yml")
    al = cy.get("alineamiento") or {}
    filas = []
    for r in al.get("resultados") or []:
        evid = [e for e in al.get("evaluaciones") or [] if r["id"] in (e.get("resultados") or [])]
        ses = []
        for s in sesiones(curso):
            sy = leer(s / "sesion.yml")
            if r["id"] in (sy.get("resultados_aprendizaje") or []):
                ses.append((s.name, sy.get("titulo", s.name), sy.get("dinamica")))
        filas.append({"resultado": r, "evidencias": evid, "sesiones": ses})
    return filas


def matriz_md(curso: Path) -> str:
    out = ["| resultado | evidencia (evaluación) | actividad (sesión) |", "|---|---|---|"]
    for f in filas_matriz(curso):
        r = f["resultado"]
        ev = "; ".join(f"{e['titulo']} ({e['tipo']}{', ' + num(e['peso']) + ' %' if e.get('peso') else ''})"
                       for e in f["evidencias"]) or "**falta**"
        se = "; ".join(f"{n}{' (activa)' if d else ''}" for n, _, d in f["sesiones"]) or "**falta**"
        out.append(f"| {r['id']}: {r['enunciado']} | {ev} | {se} |")
    out.append(f"\n<sub>Por qué: alineamiento constructivo · {FUENTE['alineamiento']}</sub>")
    return "\n".join(out) + "\n"


def tabla_partida(columnas: str, cabecera: str, filas: list[str]) -> list[str]:
    """Una tabla como una pila de tabularx de una fila: la página puede cortar entre filas sin paquetes nuevos."""
    out = [r"\noindent\begin{tabularx}{\linewidth}{" + columnas + "}", r"\toprule", cabecera + r" \\", r"\end{tabularx}\par"]
    for i, f in enumerate(filas):
        regla = r"\bottomrule" if i == len(filas) - 1 else r"\midrule"
        out += [r"\nointerlineskip\noindent\begin{tabularx}{\linewidth}{" + columnas + "}", r"\midrule" if i == 0 else "",
                f + r" \\", regla, r"\end{tabularx}\par"]
    return [x for x in out if x]


IZQ = r">{\raggedright\arraybackslash}"


def matriz_tex(curso: Path) -> str:
    filas = []
    for f in filas_matriz(curso):
        r = f["resultado"]
        ev = r" \newline ".join(
            f"{tex(e['titulo'])} ({tex(e['tipo'])}{', ' + num(e['peso']) + r' \%' if e.get('peso') else ''})"
            for e in f["evidencias"]) or r"\textbf{falta}"
        se = r" \newline ".join(f"{tex(t)}{' (aprendizaje activo)' if d else ''}" for _, t, d in f["sesiones"]) \
            or r"\textbf{falta}"
        nivel = f" \\newline {{\\footnotesize SOLO: {r['nivel'].replace('_', ' ')}}}" if r.get("nivel") else ""
        filas.append(rf"\textbf{{{tex(r['id'])}}}. {tex(r['enunciado'])}{nivel} & {ev} & {se}")
    columnas = rf"@{{}}{IZQ}p{{0.34\linewidth}} {IZQ}X {IZQ}X@{{}}"
    cab = r"\textbf{Resultado de aprendizaje} & \textbf{Evidencia (evaluación)} & \textbf{Actividad (sesión)}"
    return "\n".join(tabla_partida(columnas, cab, filas)) + "\n"


def rubrica_tex(rub: dict) -> str:
    esc = escala(rub)
    columnas = rf"@{{}}{IZQ}p{{0.15\linewidth}} " + " ".join([IZQ + "X"] * len(esc)) + r" r@{}"
    cab = r"\textbf{Criterio} & " + " & ".join(
        rf"\textbf{{{tex(n) or num(p)}}}{(' (' + num(p) + ')') if n else ''}" for p, n in esc) + r" & \textbf{Peso}"
    filas = []
    for c in rub["criterios"]:
        por = {n["puntaje"]: n["descriptor"] for n in c["niveles"]}
        filas.append(rf"\textbf{{{tex(c['nombre'])}}} & " + " & ".join(tex(por.get(p, "")) for p, _ in esc)
                     + rf" & {num(c['peso'])}\,\%")
    out = [MARCA_GENERADO, f"% Rúbrica «{rub.get('clave', '')}»: {rub.get('titulo', '')}", r"\begingroup\small"]
    out += tabla_partida(columnas, cab, filas)
    out += [r"\par\smallskip{\footnotesize Nota sobre 100: Σ peso × (puntaje ÷ puntaje máximo del criterio); "
            r"la vigesimal es esa nota ÷ 5. "
            rf"Por qué esta rúbrica: se comparte antes y se usa para formar, no solo para calificar · {tex(rub['fuente'])}.}}",
            r"\endgroup"]
    return "\n".join(out) + "\n"


def rubrica_md(rub: dict) -> str:
    esc = escala(rub)
    out = [f"### {rub['titulo']}", "", "| criterio | " + " | ".join(n or num(p) for p, n in esc) + " | peso |",
           "|---" * (len(esc) + 2) + "|"]
    for c in rub["criterios"]:
        por = {n["puntaje"]: n["descriptor"] for n in c["niveles"]}
        out.append(f"| {c['nombre']} | " + " | ".join(por.get(p, "") for p, _ in esc) + f" | {num(c['peso'])} % |")
    out.append(f"\n<sub>Por qué · {rub['fuente']}</sub>")
    return "\n".join(out) + "\n"


def documento_alineamiento(curso: Path) -> str:
    """El anexo del sílabo: resultados, matriz, evaluaciones con su política de IA, rúbricas y medición del curso."""
    cy = leer(curso / "curso.yml")
    al = cy["alineamiento"]
    pia = cy.get("politica_ia") or {}
    out = [MARCA_GENERADO, f"% Fuente: {curso.name}/curso.yml (alineamiento, politica_ia) y las rúbricas que declara.",
           r"\documentclass{academic-report}", r"\tipodocumento{Anexo del sílabo}",
           r"\universidad{Universidad Nacional de San Cristóbal de Huamanga}", r"\escuela{Escuela Profesional de Economía}",
           rf"\curso{{{tex(cy['titulo'])}}}", rf"\titulodocumento{{Alineamiento, evaluación y uso de IA}}",
           r"\begin{document}", r"\encabezado", "",
           r"\section*{Resultados de aprendizaje y su alineamiento}",
           rf"Cada resultado tiene la evidencia que lo comprueba y la sesión que lo trabaja (alineamiento constructivo; "
           rf"{tex(FUENTE['alineamiento'])}).", "", r"\begingroup\small", matriz_tex(curso).rstrip(), r"\endgroup", "",
           r"\section*{Evaluaciones}", r"\begingroup\small",
           r"\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}X c c@{}}", r"\toprule",
           r"\textbf{Evaluación} & \textbf{Tipo} & \textbf{Peso} \\\midrule"]
    for e in al.get("evaluaciones") or []:
        peso = num(e["peso"]) + r"\,\%" if e.get("peso") else "--"
        out.append(rf"{tex(e['titulo'])} & {tex(e['tipo'])} & {peso} \\")
    out += [r"\bottomrule", r"\end{tabularx}", r"\endgroup", ""]
    if pia.get("regla"):
        out += [r"\section*{Política de uso de la inteligencia artificial}",
                r"\input{../politica-ia.tex}", ""]
    ec = al.get("evaluacion_curso")
    if ec:
        out += [r"\section*{Evaluación del propio curso}",
                tex(ec.get("descripcion", "")) + " Resultados clave: " +
                ", ".join(tex(x) for x in ec.get("resultados") or []) + ".",
                rf"{{\footnotesize Por qué · {tex(ec.get('fuente', FUENTE['curso']))}.}}", ""]
    # una rúbrica por archivo, aunque la usen varias evaluaciones (la de réplica sirve a la ronda de pares y al informe)
    rubs: dict[Path, list[dict]] = {}
    for e in al.get("evaluaciones") or []:
        if e.get("rubrica"):
            rubs.setdefault(curso / e["rubrica"], []).append(e)
    if rubs:
        out.append(r"\section*{Rúbricas}")
        for ruta, evs in rubs.items():
            rub = leer(ruta)
            usan = "; ".join(tex(e["titulo"]) for e in evs)
            out += [rf"\subsection*{{{tex(rub['titulo'])}}}",
                    rf"{{\footnotesize La usa{'n' if len(evs) > 1 else ''}: {usan}.}}\par\smallskip",
                    rf"\input{{{os.path.relpath(ruta.with_suffix('.tex'), curso / '01-diseno' / 'alineamiento')}}}", ""]
    out += [r"\end{document}"]
    return "\n".join(out) + "\n"


def politica_ia_tex(curso: Path) -> str:
    """El fragmento de la política de IA (`curso.yml` → `politica_ia` y el uso de cada evaluación), sin título.

    Lo incluyen la sección «Uso de la inteligencia artificial» del sílabo (`templates/report/silabo/`, con
    `\\InputIfFileExists{politica-ia.tex}`) y el anexo del sílabo: una sola fuente para los dos.
    """
    cy = leer(curso / "curso.yml")
    pia = cy.get("politica_ia") or {}
    evs = (cy.get("alineamiento") or {}).get("evaluaciones") or []
    out = [MARCA_GENERADO, f"% Fuente: {curso.name}/curso.yml (politica_ia y alineamiento.evaluaciones[].politica_ia).",
           tex(pia.get("regla", "")), ""]
    if evs:
        out += [r"\begingroup\small",
                r"\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{0.38\linewidth} >{\raggedright\arraybackslash}X@{}}",
                r"\toprule", r"\textbf{Evaluación} & \textbf{Uso de IA permitido} \\\midrule"]
        for e in evs:
            pol = e.get("politica_ia", "")
            out.append(rf"{tex(e['titulo'])} & \textbf{{{tex(pol)}}}: {tex(POLITICA_IA.get(pol, ''))} \\")
        out += [r"\bottomrule", r"\end{tabularx}", r"\endgroup", ""]
    if pia.get("declaracion"):
        out += [rf"\textbf{{Cómo se declara.}} {tex(pia['declaracion'])}", ""]
    if pia.get("datos"):
        out += [rf"\textbf{{Datos que nunca van a una herramienta de IA.}} {tex(pia['datos'])}", ""]
    out += [rf"{{\footnotesize Por qué · {tex(pia.get('fuente', FUENTE['ia']))}.}}"]
    return "\n".join(out) + "\n"


def vistas(curso: Path) -> dict[Path, str]:
    """Las vistas generadas de un curso: la política de IA (si la declara) y, si está alineado, el anexo del sílabo y
    la tabla de cada rúbrica."""
    cy = leer(curso / "curso.yml")
    al = cy.get("alineamiento")
    out = {}
    if (cy.get("politica_ia") or {}).get("regla"):
        out[curso / "01-diseno" / "politica-ia.tex"] = politica_ia_tex(curso)
    if not al:
        return out
    out[curso / "01-diseno" / "alineamiento" / "alineamiento.tex"] = documento_alineamiento(curso)
    for e in al.get("evaluaciones") or []:
        if e.get("rubrica") and (curso / e["rubrica"]).is_file():
            rub = leer(curso / e["rubrica"])
            if not problemas_rubrica(rub):
                out[(curso / e["rubrica"]).with_suffix(".tex")] = rubrica_tex(rub)
    return out


# ---------------------------------------------------------------------------------------------------- banco

def cuestionario(curso: Path, sesion: Path, examen: bool, semilla: int) -> list[tuple[str, dict]]:
    """Preguntas de una clase: las de la sesión y el repaso espaciado e intercalado de las anteriores.

    Con `examen`, una muestra de todas las sesiones hasta esta, con al menos una por sesión.
    """
    orden = [s for s in sesiones(curso) if banco_de(s)]
    if sesion not in orden:
        raise SystemExit(f"{sesion.name} no tiene recuperacion.yml")
    k = orden.index(sesion)
    rnd = random.Random(semilla + k)
    elegidas = [(sesion.name, p) for p in banco_de(sesion)["preguntas"]]
    if examen:
        for s in orden[:k]:
            pr = banco_de(s)["preguntas"]
            elegidas += [(s.name, p) for p in rnd.sample(pr, min(2, len(pr)))]
        return elegidas
    for distancia, cuantas in DISTANCIAS_REPASO:
        if k - distancia >= 0:
            s = orden[k - distancia]
            pr = banco_de(s)["preguntas"]
            elegidas += [(s.name + " (repaso)", p) for p in rnd.sample(pr, min(cuantas, len(pr)))]
    return elegidas


def cuestionario_md(curso: Path, items: list[tuple[str, dict]], titulo: str, claves: bool = True) -> str:
    """El cuestionario en Markdown; con `claves=False`, la versión del estudiante (las claves se ven en la puesta en común)."""
    despues = "después compara con las claves." if claves else "las claves se revisan en la puesta en común de la clase."
    out = [f"# {titulo}", "", f"Responde sin mirar apuntes; {despues} Por qué · {FUENTE['banco']}", ""]
    for i, (origen, p) in enumerate(items, 1):
        out.append(f"{i}. ({origen}) {p['enunciado']}")
        for o in p.get("opciones") or []:
            out.append(f"    - {o}")
    if not claves:
        return "\n".join(out) + "\n"
    out += ["", "## Claves", ""]
    for i, (_, p) in enumerate(items, 1):
        out.append(f"{i}. {p['respuesta']}" + (f". {p['explicacion']}" if p.get("explicacion") else ""))
    return "\n".join(out) + "\n"


def cuestionario_tex(curso: Path, items: list[tuple[str, dict]], titulo: str, claves: bool = True) -> str:
    cy = leer(curso / "curso.yml")
    out = [r"\documentclass{academic-report}", r"\tipodocumento{Práctica de recuperación}",
           rf"\curso{{{tex(cy['titulo'])}}}", rf"\titulodocumento{{{tex(titulo)}}}", r"\begin{document}", r"\encabezado",
           (r"Responde sin mirar apuntes; después compara con las claves. " if claves else
            r"Responde sin mirar apuntes; las claves se revisan en la puesta en común de la clase. ")
           + rf"{{\footnotesize Por qué · {tex(FUENTE['banco'])}.}}",
           r"\begin{enumerate}"]
    for origen, p in items:
        out.append(rf"\item {{\footnotesize[{tex(origen)}]}} {tex(p['enunciado'])}")
        if p.get("opciones"):
            out.append(r"\begin{itemize}")
            out += [rf"\item {tex(o)}" for o in p["opciones"]]
            out.append(r"\end{itemize}")
    if not claves:
        return "\n".join(out + [r"\end{enumerate}", r"\end{document}"]) + "\n"
    out += [r"\end{enumerate}", r"\newpage", r"\section*{Claves}", r"\begin{enumerate}"]
    for _, p in items:
        out.append(rf"\item {tex(p['respuesta'])}" + (f". {tex(p['explicacion'])}" if p.get("explicacion") else ""))
    out += [r"\end{enumerate}", r"\end{document}"]
    return "\n".join(out) + "\n"


def pre_post(curso: Path) -> list[tuple[str, dict]]:
    """La prueba de antes y después: todas las preguntas de los resultados clave (dos por resultado como mínimo)."""
    ec = leer(curso / "curso.yml")["alineamiento"].get("evaluacion_curso") or {}
    clave = ec.get("resultados") or []
    return [(s.name, p) for s in sesiones(curso) for p in (banco_de(s) or {}).get("preguntas") or []
            if p.get("resultado") in clave]


# ---------------------------------------------------------------------------------------------------- órdenes

def opcion(args: list[str], nombre: str, defecto=None):
    if nombre in args:
        i = args.index(nombre)
        valor = args[i + 1]
        del args[i:i + 2]
        return valor
    return defecto


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in {"verificar", "matriz", "rubrica", "calificar", "banco", "pre-post", "generar"}:
        print(__doc__, file=sys.stderr)
        return 2
    orden, args = argv[0], list(argv[1:])
    formato = opcion(args, "--formato", "md")
    if orden == "verificar":
        rutas = [curso_dir(a) for a in args] or sorted(p.parent for p in CURSOS.glob("*/curso.yml"))
        errores = 0
        for c in rutas:
            inf = verificar_curso(c)
            for linea in inf.avisos + inf.errores:
                print(linea)
            errores += len(inf.errores)
        return 1 if errores else 0
    if orden == "matriz":
        c = curso_dir(args[0])
        print(matriz_tex(c) if formato == "tex" else matriz_md(c), end="")
        return 0
    if orden == "rubrica":
        rub = leer(Path(args[0]))
        malos = problemas_rubrica(rub)
        if malos:
            print("\n".join(f"[XX] {Path(args[0]).name}: {m}" for m in malos), file=sys.stderr)
            return 1
        print(rubrica_tex(rub) if formato == "tex" else rubrica_md(rub), end="")
        return 0
    if orden == "calificar":
        rub = leer(Path(args[0]))
        if problemas_rubrica(rub):
            print("[XX] rúbrica mal formada: corre `verificar`", file=sys.stderr)
            return 1
        with open(args[1], encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
        w = csv.writer(sys.stdout)
        w.writerow(["codigo", "nota", "nota_100", "vetos"])   # nota: vigesimal (nota_100 × 20 / 100)
        for fila in filas:
            r = calificar(rub, fila)
            w.writerow([fila.get("codigo", ""), num(r["nota"]), num(r["nota_100"]), " ".join(r["vetos"])])
        return 0
    estudiante = "--estudiante" in args   # versión del estudiante: sin claves (banco y pre-post)
    args = [a for a in args if a != "--estudiante"]
    if orden == "banco":
        examen = "--examen" in args
        args = [a for a in args if a != "--examen"]
        semilla = int(opcion(args, "--semilla", "2026"))
        c = curso_dir(args[0])
        s = sesion_dir(c, args[1])
        items = cuestionario(c, s, examen, semilla)
        titulo = f"{'Examen' if examen else 'Recuperación'}: {leer(s / 'sesion.yml').get('titulo', s.name)}"
        print(cuestionario_tex(c, items, titulo, not estudiante) if formato == "tex"
              else cuestionario_md(c, items, titulo, not estudiante), end="")
        return 0
    if orden == "pre-post":
        c = curso_dir(args[0])
        items = pre_post(c)
        titulo = "Prueba antes y después (resultados clave)"
        print(cuestionario_tex(c, items, titulo, not estudiante) if formato == "tex"
              else cuestionario_md(c, items, titulo, not estudiante), end="")
        return 0
    # generar
    aplicar = "--aplicar" in args
    c = curso_dir([a for a in args if a != "--aplicar"][0])
    cambios = 0
    for ruta, texto in vistas(c).items():
        if ruta.is_file() and ruta.read_text(encoding="utf-8") == texto:
            continue
        cambios += 1
        print(f"{'escribe' if aplicar else 'escribiría'} {ruta.relative_to(c)}")
        if aplicar:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(texto, encoding="utf-8")
    print(f"{cambios} vista(s) {'escritas' if aplicar else 'por escribir (simulación; --aplicar para escribir)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
