#!/usr/bin/env python3
"""
temario.py — El currículo de cada curso vive UNA sola vez en `temario.yml`
(F5.1, 2026-09-06). Desde ahí se generan todas las vistas.

Uso (desde cualquier sitio; opera sobre todas las áreas o sobre los cursos indicados):
  temario.py migrar   [--aplicar] [CURSO_DIR ...]   README/02_CONTENIDO → temario.yml (unidades y temas)
  temario.py generar  [--aplicar] [--que readme,esqueleto,web,skill,resumen] [CURSO_DIR ...]
  temario.py verificar [CURSO_DIR ...]              exit 1 si el README de algún curso no coincide con su temario

Vistas generadas (`generar`):
  readme     README.md del curso (formato canónico del estándar 00–09)
  esqueleto  02_CONTENIDO/Unidad_NN/<n m tema>.md que falten (nunca sobrescribe)
  web        04 index/cursos/<web_slug>/index.qmd: sección «Contenidos / Sílabo» entre marcadores
  skill      prompts/learning-skill/2 domains/_temarios/<dominio>.md + puntero en el dominio
  resumen    05 tasks/temarios cursos (generado).md — checklist por curso/unidad/tema

Sin --aplicar todo es simulación: se imprime qué cambiaría y no se escribe nada.
Dependencias: python3 ≥ 3.9, pyyaml.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

FW = Path(__file__).resolve().parents[1]           # …/10 Class
DOCS = FW.parent                                    # …/Documents
AREAS = FW / "areas"
WEB_CURSOS = DOCS / "04 index" / "cursos"
DOMINIOS = DOCS / "prompts" / "learning-skill" / "2 domains"
TAREAS = DOCS / "05 tasks"

EMOJI_DEFAULT = "📘"
MARCA_INI, MARCA_FIN = "<!-- temario:inicio (generado por 10 Class/scripts/temario.py; no editar a mano) -->", "<!-- temario:fin -->"
PUNTERO_SKILL = "<!-- temario.yml -->"
PLACEHOLDER_DESC = re.compile(r"^(Estructura 00–09\.?|Curso( completo)? \(estructura 00–09\)\.?)$")

# Correspondencias que no se deducen del nombre (curso → dominio FUAT)
DOMINIO_OVERRIDE = {
    "crecimiento_economico": "crecimiento_desarrollo",
    "economia_del_desarrollo": "crecimiento_desarrollo",
    "economia_de_los_rrnn_y_ambientales": "recursos_naturales_ambientales",
    "evaluacion_privada_de_proyectos": "evaluacion_proyectos",
    "evaluacion_social_de_proyectos": "evaluacion_proyectos",
    "formulacion_de_proyectos": "evaluacion_proyectos",
    "estadistica": "econometria",
    "estadistica_para_economistas": "econometria",
    "economia_rrnn_ambientales": "recursos_naturales_ambientales",
    "evaluacion_social_proyectos": "evaluacion_proyectos",
    "economia_politica": "humanidades_ciencias_sociales",
    "filosofia_politica": "humanidades_ciencias_sociales",
    "sistema_apa": "lectura_academica",
    "monografias": "lectura_academica",
    "ensayo": "lectura_academica",
    "seminario_de_investigacion": "lectura_academica",
}


# ---------------------------------------------------------------- utilidades
def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def slug_web(s: str) -> str:
    return slug(s).replace("_", "-")


def cursos_objetivo(args_cursos: list[str]) -> list[Path]:
    if args_cursos:
        return [Path(c).resolve() for c in args_cursos]
    return sorted(p for p in AREAS.glob("Academic_Class-*/course_*") if p.is_dir())


def leer_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def dump_yaml(d: dict) -> str:
    return yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=1000)


def dominios_disponibles() -> dict[str, Path]:
    return {p.stem: p for p in DOMINIOS.glob("*/*.md") if not p.stem.startswith("_")}


def slugs_web() -> set[str]:
    return {p.name for p in WEB_CURSOS.iterdir() if p.is_dir() and not p.name.startswith("_")} if WEB_CURSOS.is_dir() else set()


# ---------------------------------------------------------------- lectura de fuentes actuales
RE_H1 = re.compile(r"^#\s+(\S+)\s+(.+)$", re.M)
RE_UNIDAD = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*\(\d+\s+temas?\)\s*$", re.M)
RE_TEMA = re.compile(r"^-\s+`(\d+)\.(\d+)`\s+(.+?)\s*$", re.M)
RE_ARCH = re.compile(r"^(\d+)(?:\s+(\d+))?\s+(.+)\.md$")


def parse_readme(txt: str) -> dict:
    d: dict = {}
    m = RE_H1.search(txt)
    if m:
        tok, resto = m.group(1), m.group(2)
        if re.match(r"^\W+$", tok):
            d["emoji"], d["titulo"] = tok, resto.strip()
        else:
            d["emoji"], d["titulo"] = EMOJI_DEFAULT, (tok + " " + resto).strip()
    # descripción: primer párrafo tras el H1 que no sea viñeta ni encabezado
    lines = txt.split("\n")
    i = 1 if lines and lines[0].startswith("#") else 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and not lines[i].startswith(("-", "#", "|", ">")):
        desc = lines[i].strip()
        d["descripcion"] = "" if PLACEHOLDER_DESC.match(desc) else desc
    for clave, rx in (("semestre", r"\*\*Semestre:\*\*\s*(.+)$"), ("prerrequisitos", r"\*\*Prerrequisitos:\*\*\s*(.+)$"), ("etiqueta", r"\*\*Etiqueta común:\*\*\s*`([^`]+)`")):
        mm = re.search(rx, txt, re.M)
        if mm:
            d[clave] = mm.group(1).strip()
    # unidades y temas
    unidades = []
    for mu in RE_UNIDAD.finditer(txt):
        unidades.append({"id": int(mu.group(1)), "titulo": mu.group(2).strip(), "temas": []})
    por_id = {u["id"]: u for u in unidades}
    for mt in RE_TEMA.finditer(txt):
        u = por_id.get(int(mt.group(1)))
        if u is not None:
            u["temas"].append({"id": f"{mt.group(1)}.{mt.group(2)}", "titulo": mt.group(3).strip()})
    if unidades:
        d["unidades"] = unidades
    return d


def unidades_desde_carpetas(curso: Path) -> list[dict]:
    """Cursos sin README estructurado: el currículo está en 02_CONTENIDO/Unidad_NN/<n m tema>.md."""
    unidades = []
    for ud in sorted((curso / "02_CONTENIDO").glob("Unidad_*")):
        if not ud.is_dir():
            continue
        n = int(re.sub(r"\D", "", ud.name) or 0)
        temas, k = [], 0
        for f in sorted(ud.glob("*.md"), key=lambda p: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", p.name)]):
            m = RE_ARCH.match(f.name)
            if not m:
                continue
            k += 1
            sub = int(m.group(2)) if m.group(2) else k
            titulo = m.group(3).strip()
            h1 = re.search(r"^#\s+(.+)$", f.read_text(encoding="utf-8", errors="ignore"), re.M)
            if h1 and len(h1.group(1)) < 120:
                titulo = re.sub(r"^\W+", "", h1.group(1)).strip()
            temas.append({"id": f"{n}.{sub}", "titulo": titulo, "archivo": str(f.relative_to(curso))})
        if temas:
            unidades.append({"id": n, "titulo": f"Unidad {n:02d}", "temas": temas})
    return unidades


def ruta_tema(curso: Path, uid: int, tid: str, titulo: str) -> str:
    """Archivo canónico de un tema: 02_CONTENIDO/Unidad_NN/<n m titulo-en-minusculas>.md (si ya existe uno con ese prefijo, se respeta)."""
    n, m = tid.split(".")
    carpeta = curso / "02_CONTENIDO" / f"Unidad_{uid:02d}"
    if carpeta.is_dir():
        for f in carpeta.glob(f"{int(n)} {int(m)} *.md"):
            return str(f.relative_to(curso))
    nombre = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower()
    nombre = re.sub(r"[^a-z0-9 ]+", "", nombre).strip()
    return f"02_CONTENIDO/Unidad_{uid:02d}/{int(n)} {int(m)} {nombre}.md"


# ---------------------------------------------------------------- migrar
def migrar(curso: Path, aplicar: bool, webs: set[str], doms: dict[str, Path]) -> str:
    ty = curso / "temario.yml"
    base = leer_yaml(ty) if ty.exists() else {}
    rd = curso / "README.md"
    parsed = parse_readme(rd.read_text(encoding="utf-8")) if rd.exists() else {}
    t: dict = {}
    base_id = slug(re.sub(r"^course_(\d+[-_])?", "", curso.name))
    area_slug = slug(curso.parent.name.replace("Academic_Class-", ""))
    if base_id == "curso_base":
        base_id = f"{area_slug}_curso_base"          # un id único por área (python_curso_base, r_curso_base…)
    prev = base.get("curso")
    if prev in (None, "curso_base") or str(prev).startswith("course_"):
        prev = None                                   # ids inválidos de la semilla F5.0
    t["curso"] = prev or parsed.get("etiqueta") or base_id
    t["titulo"] = base.get("titulo") or parsed.get("titulo") or curso.name
    t["emoji"] = parsed.get("emoji") or base.get("emoji") or EMOJI_DEFAULT
    t["descripcion"] = base.get("descripcion") if base.get("descripcion") is not None else parsed.get("descripcion", "")
    t["area"] = base.get("area") or curso.parent.name.replace("Academic_Class-", "")
    t["rol"] = base.get("rol", "docente")
    t["nivel"] = base.get("nivel", "pregrado")
    t["semestre"] = base.get("semestre") if base.get("semestre") not in (None, "null") else parsed.get("semestre")
    pr = base.get("prerrequisitos")
    t["prerrequisitos"] = pr if pr not in (None, [], "[]") else parsed.get("prerrequisitos", "")
    t["etiqueta"] = base.get("etiqueta") or parsed.get("etiqueta") or t["curso"]
    # web_slug: por nombre (Macro I/II → macroeconomia; niveles → ediciones en la web)
    if base.get("web_slug"):
        t["web_slug"] = base["web_slug"]
    else:
        cand = slug_web(re.sub(r"\s+(i{1,3}|iv)$", "", t["titulo"].strip(), flags=re.I))
        if cand not in webs and t["curso"].endswith("_curso_base") and slug_web(t["area"]) in webs:
            cand = slug_web(t["area"])                   # python — Curso Base → web python
        t["web_slug"] = cand if cand in webs else None
    # dominio FUAT
    if base.get("dominio_fuat"):
        t["dominio_fuat"] = base["dominio_fuat"]
    else:
        cid = t["curso"]
        cand = DOMINIO_OVERRIDE.get(cid) or re.sub(r"_(i{1,3}|iv)$", "", cid)
        if cand not in doms:
            cand2 = slug(t["area"])
            cand = cand2 if cand2 in doms else None
        t["dominio_fuat"] = cand
    # unidades
    unidades = base.get("unidades") or parsed.get("unidades") or unidades_desde_carpetas(curso)
    for u in unidades:
        for tema in u["temas"]:
            tema.setdefault("archivo", ruta_tema(curso, int(u["id"]), str(tema["id"]), tema["titulo"]))
    t["unidades"] = unidades
    t["dictados"] = base.get("dictados") or [p.name for p in sorted((curso / "09_SEMESTRES").glob("*")) if p.is_dir()]
    texto = ("# temario.yml — FUENTE ÚNICA del currículo de este curso (F5.1, 2026-09-06).\n"
             "# Se editan aquí unidades, temas y recursos; README, esqueletos de 02_CONTENIDO, ficha web,\n"
             "# temario del learning-skill y checklist de estudio se GENERAN con: 10 Class/scripts/temario-generar.sh\n"
             + dump_yaml(t))
    ntemas = sum(len(u["temas"]) for u in unidades)
    estado = f"{t['curso']:<40} unidades={len(unidades):<2} temas={ntemas:<3} web={t['web_slug'] or '-':<32} dominio={t['dominio_fuat'] or '-'}"
    if aplicar:
        ty.write_text(texto, encoding="utf-8")
    return estado


# ---------------------------------------------------------------- generadores
def render_readme(t: dict) -> str:
    total = sum(len(u["temas"]) for u in t.get("unidades", []))
    out = [f"# {t.get('emoji', EMOJI_DEFAULT)} {t['titulo']}", ""]
    if t.get("descripcion"):
        out += [t["descripcion"], ""]
    if t.get("semestre") not in (None, ""):
        out.append(f"- **Semestre:** {t['semestre']}")
    if t.get("prerrequisitos"):
        out.append(f"- **Prerrequisitos:** {t['prerrequisitos']}")
    out.append(f"- **Etiqueta común:** `{t['etiqueta']}`")
    out.append(f"- **Total de temas:** {total}")
    out += ["", "## Estructura", ""]
    for u in t.get("unidades", []):
        n = len(u["temas"])
        out.append(f"### {u['id']}. {u['titulo']} ({n} tema{'s' if n != 1 else ''})")
        out.append("")
        for tema in u["temas"]:
            out.append(f"- `{tema['id']}` {tema['titulo']}")
        out.append("")
    out += ["## Metadata de cada archivo", "",
            f"Cada `.md` comienza con un frontmatter YAML con dos etiquetas: una común (`{t['etiqueta']}`) y otra específica del tema en `snake_case`.",
            "", "```yaml", "---", 'title: "..."', "tags:", f"  - {t['etiqueta']}", "  - <tema>", "---", "```", "",
            "> Este README se genera desde `temario.yml` (`10 Class/scripts/temario-generar.sh`). Edita el temario, no este archivo.", ""]
    return "\n".join(out)


def generar_readme(curso: Path, t: dict, aplicar: bool) -> str:
    if not t.get("unidades"):
        return "sin unidades: README intacto"
    nuevo = render_readme(t)
    rd = curso / "README.md"
    actual = rd.read_text(encoding="utf-8") if rd.exists() else ""
    if actual == nuevo:
        return "= README al día"
    if aplicar:
        rd.write_text(nuevo, encoding="utf-8")
    return "→ README regenerado" if aplicar else "→ README cambiaría"


def generar_esqueleto(curso: Path, t: dict, aplicar: bool) -> str:
    creados = 0
    for u in t.get("unidades", []):
        for tema in u["temas"]:
            f = curso / tema["archivo"]
            if f.exists():
                continue
            creados += 1
            if aplicar:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(f'---\ntitle: "{tema["titulo"]}"\ntags:\n  - {t["etiqueta"]}\n  - {slug(tema["titulo"])}\n---\n\n# {tema["titulo"]}\n\n> Tema `{tema["id"]}` de {t["titulo"]} (esqueleto generado desde temario.yml).\n', encoding="utf-8")
    return f"esqueletos {'creados' if aplicar else 'por crear'}: {creados}"


def bloque_temario_md(t: dict, rutas_desde: Path | None, curso_dir: Path) -> list[str]:
    out = []
    for u in t.get("unidades", []):
        out.append(f"**{u['id']}. {u['titulo']}**")
        out.append("")
        for tema in u["temas"]:
            out.append(f"- `{tema['id']}` {tema['titulo']}")
        out.append("")
    return out


def generar_web(cursos_t: list[tuple[Path, dict]], aplicar: bool) -> list[str]:
    """Una ficha web puede agrupar varios cursos (macroeconomia ← Macro I y II)."""
    por_slug: dict[str, list[tuple[Path, dict]]] = {}
    for c, t in cursos_t:
        if t.get("web_slug"):
            por_slug.setdefault(t["web_slug"], []).append((c, t))
    salida = []
    for s, lst in sorted(por_slug.items()):
        idx = WEB_CURSOS / s / "index.qmd"
        if not idx.exists():
            salida.append(f"  web {s}: sin index.qmd (se genera en F5.2)")
            continue
        txt = idx.read_text(encoding="utf-8")
        bloque = [MARCA_INI, ""]
        for c, t in lst:
            bloque.append(f"### {t['titulo']}")
            bloque.append("")
            bloque += bloque_temario_md(t, None, c)
            bloque.append(f"_Fuente: `{c.relative_to(DOCS)}/temario.yml`._")
            bloque.append("")
        bloque.append(MARCA_FIN)
        nuevo_bloque = "\n".join(bloque)
        if MARCA_INI in txt:
            nuevo = re.sub(re.escape(MARCA_INI) + r".*?" + re.escape(MARCA_FIN), lambda _: nuevo_bloque, txt, flags=re.S)
        else:
            # sustituir el cuerpo de «## Contenidos / Sílabo» hasta el siguiente encabezado
            m = re.search(r"(## Contenidos / Sílabo\s*\n)(.*?)(?=\n## )", txt, re.S)
            if not m:
                salida.append(f"  web {s}: sin sección «Contenidos / Sílabo»; no se toca")
                continue
            nuevo = txt[:m.end(1)] + "\n" + nuevo_bloque + "\n" + txt[m.end(2):]
        if nuevo != txt:
            if aplicar:
                idx.write_text(nuevo, encoding="utf-8")
            salida.append(f"  web {s}: {'actualizada' if aplicar else 'cambiaría'} ({len(lst)} curso(s))")
        else:
            salida.append(f"  web {s}: al día")
    return salida


def generar_skill(cursos_t: list[tuple[Path, dict]], aplicar: bool) -> list[str]:
    doms = dominios_disponibles()
    por_dom: dict[str, list[tuple[Path, dict]]] = {}
    for c, t in cursos_t:
        if t.get("dominio_fuat") in doms:
            por_dom.setdefault(t["dominio_fuat"], []).append((c, t))
    salida = []
    gen_dir = DOMINIOS / "_temarios"
    for d, lst in sorted(por_dom.items()):
        out = [f"# Temario oficial — dominio `{d}`", "",
               "> Generado por `10 Class/scripts/temario.py` desde el `temario.yml` de cada curso (F5.1). No editar: edita el temario del curso.", ""]
        for c, t in lst:
            out.append(f"## {t['titulo']} (`{t['curso']}`, área {t['area']})")
            out.append("")
            out += bloque_temario_md(t, None, c)
            out.append(f"Archivos de tema: `{c.relative_to(DOCS)}/02_CONTENIDO/`")
            out.append("")
        gen = gen_dir / f"{d}.md"
        nuevo = "\n".join(out)
        cambio = (not gen.exists()) or gen.read_text(encoding="utf-8") != nuevo
        if cambio and aplicar:
            gen_dir.mkdir(exist_ok=True)
            gen.write_text(nuevo, encoding="utf-8")
        # puntero en el dominio (una sola vez, tras «## Temario»)
        dom = doms[d]
        txt = dom.read_text(encoding="utf-8")
        if PUNTERO_SKILL not in txt and "## Temario" in txt:
            puntero = (f"## Temario\n\n{PUNTERO_SKILL}\n> **Temario oficial (fuente única):** [`_temarios/{d}.md`](../_temarios/{d}.md), generado desde el `temario.yml` "
                       f"de: {', '.join(t['titulo'] for _, t in lst)}. Lo que sigue es la guía didáctica por bloques del dominio; si un tema no está en el temario oficial, no forma parte del curso.\n")
            txt2 = txt.replace("## Temario\n", puntero, 1)
            if aplicar:
                dom.write_text(txt2, encoding="utf-8")
            salida.append(f"  skill {d}: include {'escrito' if aplicar else 'por escribir'} + puntero {'insertado' if aplicar else 'por insertar'} ({len(lst)} curso(s))")
        else:
            salida.append(f"  skill {d}: include {'actualizado' if cambio and aplicar else ('cambiaría' if cambio else 'al día')}; puntero presente")
    sin = [t["curso"] for _, t in cursos_t if not t.get("dominio_fuat")]
    if sin:
        salida.append(f"  sin dominio FUAT ({len(sin)}): {', '.join(sin)}")
    return salida


def generar_resumen(cursos_t: list[tuple[Path, dict]], aplicar: bool) -> str:
    out = ["---", "tags: [temarios, generado]", "---", "", "# Temarios de los cursos (generado)", "",
           "> Generado por `10 Class/scripts/temario.py` desde cada `temario.yml`. El tablero vivo de estudio sigue en `kanban cursos.md`; este archivo es la vista completa por curso/unidad/tema.", ""]
    for c, t in cursos_t:
        out.append(f"## {t.get('emoji', EMOJI_DEFAULT)} {t['titulo']} — `{t['curso']}` ({t['area']})")
        out.append("")
        for u in t.get("unidades", []):
            out.append(f"- **{u['id']}. {u['titulo']}**")
            for tema in u["temas"]:
                out.append(f"  - [ ] `{tema['id']}` [{tema['titulo']}](<../10 Class/areas/{c.parent.name}/{c.name}/{tema['archivo']}>)")
        out.append("")
    f = TAREAS / "temarios cursos (generado).md"
    nuevo = "\n".join(out)
    if f.exists() and f.read_text(encoding="utf-8") == nuevo:
        return "resumen: al día"
    if aplicar:
        f.write_text(nuevo, encoding="utf-8")
    return f"resumen: {'escrito' if aplicar else 'cambiaría'} ({f.relative_to(DOCS)})"


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["migrar", "generar", "verificar"])
    ap.add_argument("cursos", nargs="*")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--que", default="readme,esqueleto,web,skill,resumen")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    cursos = cursos_objetivo(a.cursos)
    log = (lambda *x: None) if a.quiet else print

    if a.accion == "migrar":
        webs, doms = slugs_web(), dominios_disponibles()
        estados = [migrar(c, a.aplicar, webs, doms) for c in cursos]
        for e in estados:
            log(e)
        # ids duplicados entre áreas → sufijo de área (solo si se aplicó)
        if a.aplicar:
            ids: dict[str, list[Path]] = {}
            for c in cursos:
                ty = c / "temario.yml"
                if ty.exists():
                    ids.setdefault(leer_yaml(ty)["curso"], []).append(c)
            for cid, lst in ids.items():
                if len(lst) > 1:
                    for c in lst:
                        t = leer_yaml(c / "temario.yml"); t["curso"] = f"{cid}_{slug(t['area'])}"; t["etiqueta"] = t["curso"]
                        (c / "temario.yml").write_text((c / "temario.yml").read_text(encoding="utf-8").split("\n", 3)[0] + "\n" + "\n".join((c / "temario.yml").read_text(encoding="utf-8").split("\n", 3)[1:3]) + "\n" + dump_yaml(t), encoding="utf-8")
                        log(f"  id duplicado «{cid}» → {t['curso']} ({c.name})")
        log(f"\n{'ESCRITOS' if a.aplicar else 'SIMULACIÓN'}: {len(cursos)} temario.yml")
        return 0

    cursos_t = [(c, leer_yaml(c / "temario.yml")) for c in cursos if (c / "temario.yml").exists()]
    if a.accion == "verificar":
        drift = 0
        for c, t in cursos_t:
            rd = c / "README.md"
            if not t.get("unidades"):
                log(f"  sin unidades (temario por completar): {c.relative_to(DOCS)}")
                continue
            if not rd.exists() or rd.read_text(encoding="utf-8") != render_readme(t):
                drift += 1
                log(f"  README desfasado: {c.relative_to(DOCS)}")
            faltan = [x["archivo"] for u in t.get("unidades", []) for x in u["temas"] if not (c / x["archivo"]).exists()]
            if faltan:
                log(f"  {len(faltan)} archivo(s) de tema sin crear en {c.name} (ejecuta generar --que esqueleto)")
        log(f"{'OK' if drift == 0 else 'DRIFT'}: {len(cursos_t)} cursos, {drift} README desfasados")
        return 1 if drift else 0

    que = set(a.que.split(","))
    for c, t in cursos_t:
        partes = []
        if "readme" in que:
            partes.append(generar_readme(c, t, a.aplicar))
        if "esqueleto" in que:
            partes.append(generar_esqueleto(c, t, a.aplicar))
        log(f"{t['curso']:<40} " + " · ".join(partes))
    if "web" in que:
        log("\n".join(generar_web(cursos_t, a.aplicar)))
    if "skill" in que:
        log("\n".join(generar_skill(cursos_t, a.aplicar)))
    if "resumen" in que:
        log(generar_resumen(cursos_t, a.aplicar))
    log(f"\n{'APLICADO' if a.aplicar else 'SIMULACIÓN (usa --aplicar)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
