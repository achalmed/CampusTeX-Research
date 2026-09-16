#!/usr/bin/env python3
"""
enlazar.py — Enlaza el currículo (curso.yml) con lo que ya existe fuera del framework (F5.3, 2026-09-06; M5 2026-09-15).

  enlazar.py posts       [--aplicar]   cada post de 04 index/_pubs declara `curso: <id>` (por su carpeta temática)
  enlazar.py simuladores [--aplicar]   modelos de 02 analysis/simuladores → recursos {tipo: simulador} del tema (por similitud de título)
  enlazar.py examenes    [--aplicar]   subcarpetas de 04-evaluaciones/ del curso → `banco_examenes` (R10, 2026-09-15)
  enlazar.py verificar                 recursos y bancos con rutas existentes; posts con curso desconocido; posts sin curso

Sin --aplicar todo es simulación (imprime qué haría). Las correspondencias que no se deducen se declaran en las
tablas MAPA_POSTS y MAPA_BANCO de este archivo; la de simuladores se calcula (y se lista para revisión).
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path

import yaml

FW = Path(__file__).resolve().parents[1]
DOCS = FW.parent
CURSOS = FW / "docencia" / "cursos"     # M5 (2026-09-15): docencia/cursos/<slug>/curso.yml
PUBS = DOCS / "04 index" / "_pubs"
LAB = DOCS / "02 analysis" / "simuladores"

# blog → {carpeta temática (o 'posts'): curso}. None = sin curso equivalente (se deja sin enlazar).
MAPA_POSTS: dict[str, dict[str, str | None]] = {
    "pub_numerus-scriptum": {"python": "python_curso_base", "r": "r_curso_base", "stata": "stata_curso_base", "eviews": "eviews_curso_base",
                             "latex": "latex_curso_base", "ofimatica": "ofimatica_curso_base", "power-bi": "ofimatica_curso_base",
                             "fundamentos-programacion": "programming_concepts_curso_base", "matlab": None, "cpp": None, "bloomberg": None, "posts": None},
    "pub_epsilon-y-beta": {"00-econometria-general": "econometria_i", "01-fundamentos-econometria": "econometria_i", "02-macroeconometria": "econometria_ii",
                           "03-microeconometria": "microeconometria_aplicada", "04-econometria-financiera": "econometria_ii", "05-econometria-bayesiana": "econometria_ii",
                           "06-evaluacion-de-impacto": "microeconometria_aplicada", "07-topicos-de-econometria": "econometria_ii",
                           "estadistica-para-economistas": "estadistica_para_economistas", "estadistica": "estadistica", "posts": "econometria_i"},
    "pub_axiomata": {"economia-matematica": "matematicas_i", "posts": "matematicas_i"},
    "pub_aequilibria": {"posts": "macroeconomia_i"},
    "pub_optimums": {"organizacion-industrial": "organizacion_industrial", "posts": "microeconomia_i"},
    "pub_pecunia-fluxus": {"finanzas-internacionales": "finanzas_iii", "posts": "finanzas_i"},
    "pub_methodica": {"posts": "monografias"},
    "pub_res-publica": {"posts": "economia_publica"},
    "pub_actus-mercator": {"inteligencia-comercial": "investigacion_de_mercados", "posts": "formulacion_de_proyectos"},
    "pub_dialectica-y-mercado": {"posts": "economia_politica"},
    "pub_chaska": {"ciberseguridad-cybersoc-ccs": None, "ciberseguridad-ethical-hacking-ceh": None, "i3wm": None, "operating-system": None, "posts": None},
}

# El banco de exámenes vive dentro de cada curso desde R10 (2026-09-15): cursos/<slug>/04-evaluaciones/<sub>/
# (antes, carpetas de 01 notes/50-examenes-y-practicas mapeadas aquí por curso; el mapa de la migración está en
# docencia/migracion/migrar-examenes.py y mapa-examenes.csv). `banco/` cuenta archivos sueltos; las demás
# subcarpetas cuentan expedientes (carpetas) y .tex sueltos.
SUBS_EVALUACIONES = ("examen_parcial", "examen_final", "practicas", "laboratorios", "tareas", "proyectos", "banco", "soluciones")

# a qué cursos puede enlazarse cada disciplina del laboratorio (evita falsos positivos: «rango» de matrices, «median» de R…)
DISCIPLINA_CURSOS = {
    "macro": {"macroeconomia_i", "macroeconomia_ii", "macroeconomia_dinamica", "economia_monetaria", "crecimiento_economico", "economia_del_desarrollo",
              "comercio_internacional", "economia_computacional", "economia_publica"},
    "estadistica": {"estadistica", "estadistica_para_economistas", "econometria_i", "econometria_ii", "microeconometria_aplicada"},
}

STOP = {"de", "del", "la", "el", "los", "las", "y", "e", "o", "en", "a", "al", "con", "por", "para", "un", "una", "modelo", "curva", "teoria"}


def norm(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    toks = {t for t in re.split(r"[^a-z0-9]+", s) if len(t) > 2 and t not in STOP}
    return {t[:6] for t in toks}   # raíz aproximada


def leer_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def dump_temario(p: Path, t: dict) -> None:
    cab = p.read_text(encoding="utf-8").split("\n")
    comentarios = [l for l in cab[:3] if l.startswith("#")]
    p.write_text("\n".join(comentarios) + "\n" + yaml.safe_dump(t, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")


def cursos() -> dict[str, tuple[Path, dict]]:
    out = {}
    for ty in sorted(CURSOS.glob("*/curso.yml")):
        t = leer_yaml(ty)
        out[t.get("id") or t["curso"]] = (ty.parent, t)      # `curso` → `id` (NORMATIVA §7, M7)
        for al in t.get("alias", []) or []:                 # M4: los posts aún citan el id antiguo (M6 los reescribe)
            out.setdefault(al, (ty.parent, t))
    return out


# ---------------------------------------------------------------- posts
def posts_iter():
    for blog in sorted(PUBS.glob("pub_*")):
        for idx in blog.rglob("index.qmd"):
            rel = idx.relative_to(blog)
            if any(part in ("_site", "_freeze", "_extensions", ".quarto") for part in rel.parts):
                continue
            if len(rel.parts) < 3:            # <tema>/<post>/index.qmd
                continue
            if not re.match(r"^\d{4}-\d{2}-\d{2}-", rel.parts[-2]):
                continue
            yield blog.name, rel.parts[0], idx


def frontmatter_set(idx: Path, clave: str, valor: str) -> bool:
    txt = idx.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return False
    fm = m.group(1)
    if re.search(rf"^{clave}:", fm, re.M):
        return False
    nuevo = "---\n" + fm + f"\n{clave}: {valor}\n---\n" + txt[m.end():]
    idx.write_text(nuevo, encoding="utf-8")
    return True


def cmd_posts(aplicar: bool, ids: set[str]) -> None:
    n_ok = n_ya = n_sin = 0
    sin: dict[str, int] = {}
    for blog, carpeta, idx in posts_iter():
        curso = MAPA_POSTS.get(blog, {}).get(carpeta, "?")
        if curso == "?":
            sin[f"{blog}/{carpeta}"] = sin.get(f"{blog}/{carpeta}", 0) + 1
            continue
        if curso is None:
            n_sin += 1
            continue
        if curso not in ids:
            print(f"  curso desconocido en MAPA_POSTS: {curso} ({blog}/{carpeta})"); continue
        txt = idx.read_text(encoding="utf-8")
        if re.search(r"^curso:", txt.split("\n---", 2)[1] if "\n---" in txt else "", re.M):
            n_ya += 1; continue
        if aplicar:
            frontmatter_set(idx, "curso", curso)
        n_ok += 1
    for k, v in sorted(sin.items()):
        print(f"  carpeta sin entrada en MAPA_POSTS: {k} ({v} posts)")
    print(f"posts {'enlazados' if aplicar else 'por enlazar'}={n_ok} · ya tenían curso={n_ya} · sin curso equivalente (a propósito)={n_sin}")


def posts_por_curso() -> dict[str, list[tuple[str, str, str]]]:
    """curso → [(blog, ruta relativa, título)]."""
    out: dict[str, list] = {}
    for blog, carpeta, idx in posts_iter():
        txt = idx.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
        if not m:
            continue
        fm = m.group(1)
        c = re.search(r"^curso:\s*(\S+)", fm, re.M)
        if not c:
            continue
        ti = re.search(r"^title:\s*(.+)$", fm, re.M)
        titulo = ti.group(1).strip().strip('"') if ti else idx.parent.name
        out.setdefault(c.group(1), []).append((blog, str(idx.parent.relative_to(PUBS / blog)), titulo))
    return out


# ---------------------------------------------------------------- simuladores
def modelos_lab() -> list[dict]:
    res = []
    for disc in ("macro", "estadistica"):
        for f in sorted((LAB / disc / "modelos").rglob("*.py")):
            if f.name.startswith("_"):
                continue
            s = f.read_text(encoding="utf-8", errors="ignore")
            mid = re.search(r'\bid\s*=\s*"([^"]+)"', s); nom = re.search(r'\bnombre\s*=\s*"([^"]+)"', s); niv = re.search(r"\bnivel\s*=\s*(\d+)", s)
            if mid and nom:
                res.append({"laboratorio": disc, "modelo": mid.group(1), "archivo": str(f.relative_to(DOCS)), "nombre": nom.group(1), "nivel": int(niv.group(1)) if niv else None})
    return res


def cmd_simuladores(aplicar: bool, cs: dict, umbral: float = 0.5) -> None:
    modelos = modelos_lab()
    # candidatos: temas de todos los cursos; se prefiere el mejor solape de tokens
    temas = []
    for cid, (cdir, t) in cs.items():
        for u in t.get("unidades", []):
            for tema in u["temas"]:
                temas.append((cid, u, tema, norm(tema["titulo"])))
    asignados = 0; sin = []
    cambios: dict[str, dict] = {}
    for m in modelos:
        nm = norm(m["nombre"]) | norm(m["modelo"].split("_", 1)[-1].replace("_", " "))
        mejor, best = None, 0.0
        permitidos = DISCIPLINA_CURSOS.get(m["laboratorio"])
        for cid, u, tema, nt in temas:
            if not nt or (permitidos and cid not in permitidos):
                continue
            j = len(nm & nt) / len(nm | nt)
            if j > best:
                mejor, best = (cid, u, tema), j
        if mejor and best >= umbral:
            cid, u, tema = mejor
            rec = {"tipo": "simulador", "laboratorio": m["laboratorio"], "modelo": m["modelo"], "nombre": m["nombre"], "archivo": m["archivo"]}
            ya = any(r.get("modelo") == m["modelo"] for r in tema.get("recursos", []))
            print(f"  {m['modelo']:<32} → {cid}:{tema['id']} «{tema['titulo']}»  (j={best:.2f}){'  [ya]' if ya else ''}")
            if not ya:
                tema.setdefault("recursos", []).append(rec); cambios[cid] = cs[cid][1]; asignados += 1
        else:
            sin.append(f"{m['modelo']} «{m['nombre']}»" + (f" (mejor {best:.2f})" if mejor else ""))
    if aplicar:
        for cid, t in cambios.items():
            dump_temario(cs[cid][0] / "curso.yml", t)
    print(f"modelos={len(modelos)} · {'asignados' if aplicar else 'asignables'}={asignados} · sin tema con similitud ≥{umbral}: {len(sin)}")
    for s in sin:
        print(f"    sin asignar: {s}")


# ---------------------------------------------------------------- exámenes
def cmd_examenes(aplicar: bool, cs: dict) -> None:
    n = 0
    vistos = set()
    for cid, (cdir, t) in sorted(cs.items()):
        if cdir in vistos:           # los alias apuntan al mismo curso
            continue
        vistos.add(cdir)
        ev = cdir / "04-evaluaciones"
        nuevo = []
        if ev.is_dir():
            for sub in sorted(p for p in ev.iterdir() if p.is_dir()):
                if sub.name not in SUBS_EVALUACIONES:
                    print(f"  subcarpeta fuera de la lista de new-evaluacion.sh: {cid}/04-evaluaciones/{sub.name}")
                if sub.name == "banco":
                    n_exp = sum(1 for p in sub.iterdir() if p.is_file() and not p.name.startswith("."))
                else:
                    n_exp = sum(1 for p in sub.iterdir() if p.is_dir() or p.suffix == ".tex")
                if n_exp:
                    nuevo.append({"ruta": f"04-evaluaciones/{sub.name}", "expedientes": n_exp})
        if (t.get("banco_examenes") or []) != nuevo:
            t["banco_examenes"] = nuevo; n += 1
            resumen = ", ".join(f"{b['ruta'].split('/')[-1]} ({b['expedientes']})" for b in nuevo) or "sin banco"
            print(f"  {cid:<34} ← {resumen}")
            if aplicar:
                dump_temario(cdir / "curso.yml", t)
    print(f"cursos con banco {'escrito' if aplicar else 'por escribir'}={n}")


# ---------------------------------------------------------------- verificar
def cmd_verificar(cs: dict) -> int:
    fallos = 0
    ids = set(cs)
    for cid, (cdir, t) in cs.items():
        for u in t.get("unidades", []):
            for tema in u["temas"]:
                for r in tema.get("recursos", []):
                    if "archivo" in r and not (DOCS / r["archivo"]).exists() and not (cdir / r["archivo"]).exists():
                        fallos += 1; print(f"  recurso roto: {cid}:{tema['id']} → {r['archivo']}")
        for b in t.get("banco_examenes", []) or []:
            if not (cdir / b["ruta"]).is_dir() and not (DOCS / b["ruta"]).is_dir():
                fallos += 1; print(f"  banco roto: {cid} → {b['ruta']}")
    sin = 0; desconocidos = 0
    for blog, carpeta, idx in posts_iter():
        fm = re.match(r"^---\n(.*?)\n---\n", idx.read_text(encoding="utf-8"), re.S)
        c = re.search(r"^curso:\s*(\S+)", fm.group(1), re.M) if fm else None
        if not c:
            sin += 1
        elif c.group(1) not in ids:
            desconocidos += 1; fallos += 1; print(f"  post con curso desconocido «{c.group(1)}»: {blog}/{carpeta}/{idx.parent.name}")
    print(f"{'OK' if fallos == 0 else 'FALLOS=' + str(fallos)} · posts sin curso={sin} · posts con curso desconocido={desconocidos}")
    return 1 if fallos else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["posts", "simuladores", "examenes", "verificar"])
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    cs = cursos()
    if a.accion == "posts":
        cmd_posts(a.aplicar, set(cs))
    elif a.accion == "simuladores":
        cmd_simuladores(a.aplicar, cs)
    elif a.accion == "examenes":
        cmd_examenes(a.aplicar, cs)
    else:
        return cmd_verificar(cs)
    print("APLICADO" if a.aplicar else "SIMULACIÓN (usa --aplicar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
