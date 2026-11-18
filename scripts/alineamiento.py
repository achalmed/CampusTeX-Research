#!/usr/bin/env python3
"""alineamiento.py — matriz de alineamiento, rúbricas, banco de recuperación y política de IA de un curso.

Uso:
  python3 scripts/alineamiento.py verificar [CURSO…]           # sin argumentos, todos los cursos
  python3 scripts/alineamiento.py matriz CURSO [--formato md|tex]
  python3 scripts/alineamiento.py rubrica RUBRICA.yml [--formato md|tex]
  python3 scripts/alineamiento.py calificar RUBRICA.yml PUNTAJES.csv   # columnas: codigo,<clave>,<clave>…
  python3 scripts/alineamiento.py banco CURSO SESION [--examen] [--semilla N] [--formato md|tex]
  python3 scripts/alineamiento.py pre-post CURSO [--formato md|tex]
  python3 scripts/alineamiento.py generar CURSO [--aplicar]       # vistas .tex; sin --aplicar solo simula

CURSO es el slug (contenido/cursos/<slug>) o la ruta; SESION, `sNN` o el nombre de la carpeta.
Salida: 0 bien · 1 algún error ([XX]; los avisos [!!] no hacen fallar) · 2 error de uso.

Qué verifica (docs/estandar-docencia.md §10; norma FLUJO_DE_CONOCIMIENTO, campos 10, 11 y 12):
  - Alineamiento constructivo: todo resultado con su evidencia (evaluación) y su actividad (sesión); toda
    evaluación con al menos un resultado declarado. Biggs (1996); Wiggins y McTighe (2005).
  - Rúbricas analíticas: criterios con peso (suman 100), dos o más niveles con puntaje y descriptor.
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

def problemas_rubrica(rub: dict) -> list[str]:
    """Errores de forma de una rúbrica analítica (formato común de escritura o su formato de reserva)."""
    out = []
    for k in ("titulo", "fuente", "criterios"):
        if not rub.get(k):
            out.append(f"sin `{k}`")
    crit = rub.get("criterios") or []
    claves = [c.get("clave") for c in crit]
    if len(set(claves)) != len(claves) or not all(claves):
        out.append("claves de criterio vacías o repetidas")
    try:
        total = sum(float(c.get("peso", 0)) for c in crit)
    except (TypeError, ValueError):
        total = -1
    if crit and abs(total - 100) > 1e-6:
        out.append(f"los pesos suman {total:g}, no 100")
    for c in crit:
        niv = c.get("niveles") or []
        if len(niv) < 2:
            out.append(f"criterio «{c.get('clave')}» con menos de dos niveles")
        pts = [n.get("puntaje") for n in niv]
        if any(not isinstance(p, (int, float)) for p in pts) or len(set(pts)) != len(pts):
            out.append(f"criterio «{c.get('clave')}» con puntajes no numéricos o repetidos")
        if any(not str(n.get("descriptor") or "").strip() for n in niv):
            out.append(f"criterio «{c.get('clave')}» con un nivel sin descriptor")
    return out


def escala(rub: dict) -> list[tuple[float, str]]:
    """Los puntajes de la rúbrica (de mayor a menor) con su nombre, si lo declara."""
    nombres = {e["puntaje"]: e.get("nombre", "") for e in rub.get("escala") or []}
    pts = sorted({n["puntaje"] for c in rub.get("criterios") or [] for n in c.get("niveles") or []}, reverse=True)
    return [(p, nombres.get(p, "")) for p in pts]


def calificar(rub: dict, puntajes: dict[str, float], nota_max: float = 20.0) -> float:
    """Nota de 0 a nota_max: Σ peso · (puntaje / puntaje máximo del criterio)."""
    nota = 0.0
    for c in rub["criterios"]:
        maximo = max(n["puntaje"] for n in c["niveles"])
        p = float(puntajes[c["clave"]])
        if p not in {float(n["puntaje"]) for n in c["niveles"]}:
            raise ValueError(f"puntaje {p:g} fuera de los niveles de «{c['clave']}»")
        nota += float(c["peso"]) / 100 * p / maximo
    return round(nota * nota_max, 2)


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
            ruta = curso / e["rubrica"]
            if not ruta.is_file():
                inf.error(f"evaluación «{eid}»: rúbrica «{e['rubrica']}» inexistente", "rubrica")
            else:
                rub = leer(ruta)
                for p in problemas_rubrica(rub):
                    inf.error(f"rúbrica {ruta.name}: {p}", "rubrica")
                for c in rub.get("criterios") or []:
                    if c.get("resultado") and c["resultado"] not in rs:
                        inf.error(f"rúbrica {ruta.name}: el criterio «{c.get('clave')}» mide «{c['resultado']}», "
                                  f"que la evaluación «{eid}» no declara", "alineamiento")
        elif e.get("tipo") == "sumativa" and e.get("instrumento") != "prueba":
            inf.aviso(f"evaluación sumativa «{eid}» sin rúbrica (o `instrumento: prueba`)", "rubrica")
    if evs and abs(peso_sumativo - 100) > 1e-6:
        inf.error(f"los pesos de las evaluaciones sumativas suman {peso_sumativo:g}, no 100", "alineamiento")
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
    out = [MARCA_GENERADO, f"% Rúbrica «{rub.get('id', '')}»: {rub.get('titulo', '')}", r"\begingroup\small"]
    out += tabla_partida(columnas, cab, filas)
    out += [r"\par\smallskip{\footnotesize Nota: Σ peso × (puntaje ÷ puntaje máximo del criterio) × 20. "
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
           r"\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{0.30\linewidth} c c Y@{}}", r"\toprule",
           r"\textbf{Evaluación} & \textbf{Tipo} & \textbf{Peso} & \textbf{Uso de IA permitido} \\\midrule"]
    for e in al.get("evaluaciones") or []:
        peso = num(e["peso"]) + r"\,\%" if e.get("peso") else "--"
        pol = e.get("politica_ia", "")
        out.append(rf"{tex(e['titulo'])} & {tex(e['tipo'])} & {peso} & \textbf{{{tex(pol)}}}: {tex(POLITICA_IA.get(pol, ''))} \\")
    out += [r"\bottomrule", r"\end{tabularx}", r"\endgroup", "",
            r"\section*{Política de uso de la inteligencia artificial}", tex(pia.get("regla", "")), ""]
    if pia.get("declaracion"):
        out += [rf"\textbf{{Cómo se declara.}} {tex(pia['declaracion'])}", ""]
    if pia.get("datos"):
        out += [rf"\textbf{{Datos que nunca van a una herramienta de IA.}} {tex(pia['datos'])}", ""]
    out += [rf"{{\footnotesize Por qué · {tex(pia.get('fuente', FUENTE['ia']))}.}}", ""]
    ec = al.get("evaluacion_curso")
    if ec:
        out += [r"\section*{Evaluación del propio curso}",
                tex(ec.get("descripcion", "")) + " Resultados clave: " +
                ", ".join(tex(x) for x in ec.get("resultados") or []) + ".",
                rf"{{\footnotesize Por qué · {tex(ec.get('fuente', FUENTE['curso']))}.}}", ""]
    rubs = [(e, curso / e["rubrica"]) for e in al.get("evaluaciones") or [] if e.get("rubrica")]
    if rubs:
        out.append(r"\section*{Rúbricas}")
        for e, ruta in rubs:
            rub = leer(ruta)
            out += [rf"\subsection*{{{tex(rub['titulo'])}}}", rf"\input{{{os.path.relpath(ruta.with_suffix('.tex'), curso / '01-diseno' / 'alineamiento')}}}", ""]
    out += [r"\end{document}"]
    return "\n".join(out) + "\n"


def vistas(curso: Path) -> dict[Path, str]:
    """Las vistas generadas de un curso alineado: el anexo del sílabo y la tabla de cada rúbrica."""
    cy = leer(curso / "curso.yml")
    al = cy.get("alineamiento")
    if not al:
        return {}
    out = {curso / "01-diseno" / "alineamiento" / "alineamiento.tex": documento_alineamiento(curso)}
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


def cuestionario_md(curso: Path, items: list[tuple[str, dict]], titulo: str) -> str:
    out = [f"# {titulo}", "", f"Responde sin mirar apuntes; después compara. Por qué · {FUENTE['banco']}", ""]
    for i, (origen, p) in enumerate(items, 1):
        out.append(f"{i}. ({origen}) {p['enunciado']}")
        for o in p.get("opciones") or []:
            out.append(f"    - {o}")
    out += ["", "## Claves", ""]
    for i, (_, p) in enumerate(items, 1):
        out.append(f"{i}. {p['respuesta']}" + (f". {p['explicacion']}" if p.get("explicacion") else ""))
    return "\n".join(out) + "\n"


def cuestionario_tex(curso: Path, items: list[tuple[str, dict]], titulo: str) -> str:
    cy = leer(curso / "curso.yml")
    out = [r"\documentclass{academic-report}", r"\tipodocumento{Práctica de recuperación}",
           rf"\curso{{{tex(cy['titulo'])}}}", rf"\titulodocumento{{{tex(titulo)}}}", r"\begin{document}", r"\encabezado",
           rf"Responde sin mirar apuntes; después compara con las claves. {{\footnotesize Por qué · {tex(FUENTE['banco'])}.}}",
           r"\begin{enumerate}"]
    for origen, p in items:
        out.append(rf"\item {{\footnotesize[{tex(origen)}]}} {tex(p['enunciado'])}")
        if p.get("opciones"):
            out.append(r"\begin{itemize}")
            out += [rf"\item {tex(o)}" for o in p["opciones"]]
            out.append(r"\end{itemize}")
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
        w.writerow(["codigo", "nota"])
        for fila in filas:
            w.writerow([fila.get("codigo", ""), num(calificar(rub, fila))])
        return 0
    if orden == "banco":
        examen = "--examen" in args
        args = [a for a in args if a != "--examen"]
        semilla = int(opcion(args, "--semilla", "2026"))
        c = curso_dir(args[0])
        s = sesion_dir(c, args[1])
        items = cuestionario(c, s, examen, semilla)
        titulo = f"{'Examen' if examen else 'Recuperación'}: {leer(s / 'sesion.yml').get('titulo', s.name)}"
        print(cuestionario_tex(c, items, titulo) if formato == "tex" else cuestionario_md(c, items, titulo), end="")
        return 0
    if orden == "pre-post":
        c = curso_dir(args[0])
        items = pre_post(c)
        titulo = "Prueba antes y después (resultados clave)"
        print(cuestionario_tex(c, items, titulo) if formato == "tex" else cuestionario_md(c, items, titulo), end="")
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
