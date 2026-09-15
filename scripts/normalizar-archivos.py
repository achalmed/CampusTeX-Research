#!/usr/bin/env python3
"""scripts/normalizar-archivos.py — migración M7 de la normativa de archivos en el framework y sus áreas.

Objetivo: dejar `10 Class` (framework y 23 áreas) con 0 fallos de `core/archivos.py`
  sin tocar contenido académico: registros de sesión y de curso con las claves del
  núcleo, cursos con nombre `course_NN_<slug>`, nombres de archivo en snake/kebab,
  identidad en la línea 1 de todo código propio, frontmatter con `tipo` en todo
  Markdown suelto, artefactos de TeX fuera del árbol y lo ajeno en `vendor/`.
Método: un subcomando por clase de cambio, todos simulan por defecto y listan lo
  que harían; con --aplicar escriben, renombran con `git mv` cuando el archivo está
  versionado y anotan cada paso en la bitácora (--bitacora DIR) para el UNDO.
  Reutiliza del validador (`core/archivos.py`) la detección de familia e identidad
  para actuar exactamente sobre lo que él señala.
Fundamento: meta/NORMATIVA_ARCHIVOS.md §1, §2.1, §4, §5, §6.2, §7 y fila M7 de §12;
  decisiones del encargo M7 (2026-09-15).
Alternativa: editar a mano (2 700 archivos) o un `sed` por regla. Se descarta: sin
  bitácora no hay UNDO, y sin la lógica del validador se actúa sobre lo que no toca.
Límite: no toca `04 index`, `prompts` ni `01 notes` (repos de otros agentes): imprime
  el `sed` que les corresponde. No recorre `_ESTANDARIZACION`, `vendor/` ni `.git`.
  Las notas de estudio de `02_CONTENIDO` las normaliza `normalizar-notas.py`.

Uso:
  python3 scripts/normalizar-archivos.py <subcomando> [--aplicar] [--bitacora DIR]
  subcomandos: vendor artefactos cursos nombres registros cabeceras frontmatter todo
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

FW = Path(__file__).resolve().parents[1]
AREAS = FW / "areas" if (FW / "areas").is_dir() else FW / "docencia" / "_migracion"  # M2 (2026-09-15): las áreas viven en docencia/_migracion hasta M3; M5 rehace esto
_d = FW
while _d != _d.parent and not (_d / "core" / "env.py").exists():
    _d = _d.parent
sys.path.insert(0, str(_d / "core"))
import env  # noqa: E402
import archivos as val  # noqa: E402  (el validador: familia, identidad, regexes)

DOCS = env.DOCS_ROOT
SALTAR_DIRS = val.CARPETAS_IGNORADAS | {"_ESTANDARIZACION"}     # exactamente lo que el validador no recorre
SALTAR_PREFIJO = val.CARPETAS_IGNORADAS_PREFIJO
SALTAR_SUFIJO = val.CARPETAS_IGNORADAS_SUFIJO
TEXTO_EXT = {".tex", ".md", ".qmd", ".py", ".r", ".rmd", ".do", ".sh", ".yml", ".yaml", ".txt",
             ".ipynb", ".bib", ".json", ".cls", ".sty", ".html"}
ESTADO_SESION = {"migrada": "borrador", "impartida": "hecho", "completada": "hecho", "planeada": "borrador",
                 "en_preparacion": "borrador", "lista": "activo", "planeado": "borrador"}
EXENTOS_MD = val.EXENTOS_MD | {"SECURITY.md"}

# Cursos fuera de patrón sin NN en el nombre: orden pedagógico para asignar el siguiente libre del área.
ORDEN_SIN_NN = {
    "Academic_Class-Estadistica": ["course_estadistica", "course_estadistica-para-economistas"],
    "Academic_Class-Gestion-empresarial": ["course_formulacion-de-proyectos", "course_evaluacion-privada-de-proyectos",
                                          "course_investigacion-de-mercados"],
}

BIT = {"dir": None, "aplicar": False, "plan": []}


# --- utilidades --------------------------------------------------------------
def log(msg):
    print(msg)


def bitacora(clase, *campos):
    """Anota en la bitácora (renombres.tsv · borrados.txt · modificados.txt · creados.txt) o en el plan."""
    if BIT["dir"] is None:
        return
    if not BIT["aplicar"]:
        BIT["plan"].append("\t".join([clase, *campos]))
        return
    nombre = {"mv": "renombres.tsv", "rm": "borrados.txt", "mod": "modificados.txt", "new": "creados.txt"}[clase]
    with open(Path(BIT["dir"]) / nombre, "a", encoding="utf-8") as f:
        f.write("\t".join(campos) + "\n")


def repo_de(p: Path) -> Path:
    for a in [p, *p.parents]:
        if (a / ".git").exists():
            return a
    return FW


def rel_repo(p: Path) -> str:
    return p.relative_to(repo_de(p)).as_posix()


def tracked(p: Path) -> bool:
    repo = repo_de(p)
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", str(p.relative_to(repo))],
                       capture_output=True, text=True)
    return r.returncode == 0


def git(repo: Path, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} en {repo}: {r.stderr.strip()}")


def mover(src: Path, dst: Path):
    """Renombra (git mv si está versionado). Simula si no hay --aplicar."""
    log(f"  mv  {rel_repo(src)}  →  {dst.relative_to(repo_de(src)).as_posix()}")
    bitacora("mv", str(src), str(dst))
    if not BIT["aplicar"]:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if tracked(src):
        git(repo_de(src), "mv", "-k", str(src), str(dst))
        if src.exists():                       # git mv -k no movió (p. ej. parte no versionada): mover a mano
            os.rename(src, dst)
    else:
        os.rename(src, dst)


def borrar(p: Path):
    log(f"  rm  {rel_repo(p)}")
    bitacora("rm", str(p))
    if not BIT["aplicar"]:
        return
    if tracked(p):
        git(repo_de(p), "rm", "-q", "-f", str(p))
    else:
        p.unlink()


def escribir(p: Path, texto: str, nuevo=False):
    """Escribe respetando un módulo congelado (publish-session.sh deja `publicacion/` en solo lectura)."""
    bitacora("new" if nuevo else "mod", str(p))
    if not BIT["aplicar"]:
        return
    modo = p.stat().st_mode if p.exists() else None
    congelado = modo is not None and not os.access(p, os.W_OK)
    if congelado:
        p.chmod(modo | 0o200)
    try:
        p.write_text(texto, encoding="utf-8")
    finally:
        if congelado:
            p.chmod(modo)


def leer(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def recorrer(raiz: Path, saltar: set[str] | None = None):
    saltar = SALTAR_DIRS if saltar is None else saltar
    for p in sorted(raiz.rglob("*")):
        partes = p.relative_to(raiz).parts[:-1]
        if any(x in saltar or x.startswith(SALTAR_PREFIJO) or x.endswith(SALTAR_SUFIJO) for x in partes):
            continue
        if p.is_file():
            yield p


def areas():
    return sorted(a for a in AREAS.glob("Academic_Class-*") if a.is_dir())


def cursos():
    return sorted(c for a in areas() for c in a.glob("course_*") if c.is_dir())


def ascii_min(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def kebab(nombre: str) -> str:
    base, punto, ext = nombre.rpartition(".")
    if not base:
        base, ext = ext, ""
    b = re.sub(r"[^a-z0-9]+", "-", ascii_min(base)).strip("-")
    return f"{b}.{ext.lower()}" if ext else b


def snake(nombre: str) -> str:
    base, punto, ext = nombre.rpartition(".")
    if not base:
        base, ext = ext, ""
    b = re.sub(r"[^a-z0-9]+", "_", ascii_min(base)).strip("_")
    return f"{b}.{ext.lower()}" if ext else b


def nombre_ok(nombre: str) -> bool:
    return bool(val.KEBAB.match(nombre) or val.SNAKE.match(nombre) or val.MIXTO.match(nombre))


def yaml_escalar(texto: str, clave: str):
    m = re.search(rf"^{clave}:\s*(.*)$", texto, re.M)
    return val._valor(m.group(1)) if m else None


def id_curso(curso: Path) -> str:
    t = curso / "temario.yml"
    if t.exists():
        v = yaml_escalar(leer(t), "id") or yaml_escalar(leer(t), "curso")
        if v:
            return v
    return re.sub(r"^course_(\d+[-_])?", "", curso.name)


def reemplazar_en_textos(raiz: Path, viejo: str, nuevo: str, excluir: set[Path] = frozenset()) -> int:
    """Sustituye el nombre viejo por el nuevo en los archivos de texto bajo raiz. Devuelve archivos tocados."""
    n = 0
    for p in recorrer(raiz):
        if p in excluir or p.suffix.lower() not in TEXTO_EXT:
            continue
        try:
            t = leer(p)
        except OSError:
            continue
        if viejo in t:
            escribir(p, t.replace(viejo, nuevo))
            n += 1
            log(f"      ref {rel_repo(p)}: «{viejo}» → «{nuevo}»")
    return n


# --- vendor ------------------------------------------------------------------
def cmd_vendor():
    """Plantillas LaTeX de terceros, fuentes y clases ajenas → vendor/ (el validador no lo recorre)."""
    log("== vendor")
    for c in cursos():
        pl = c / "06_RECURSOS" / "plantillas"
        if not pl.is_dir():
            continue
        vend = c / "06_RECURSOS" / "vendor"
        nombres = []
        for hijo in sorted(pl.iterdir()):
            dst = vend / hijo.name if hijo.is_dir() else vend / "plantillas" / hijo.name
            mover(hijo, dst)
            nombres.append(hijo.name)
        if BIT["aplicar"] and pl.exists() and not any(pl.iterdir()):
            pl.rmdir()
        # se anota en el registro del curso (temario.yml → README generado): el material ajeno y por qué está ahí
        ty = c / "temario.yml"
        if ty.exists() and "\najeno:" not in leer(ty):
            desc = "material de terceros conservado tal cual, sin cabecera propia (NORMATIVA_ARCHIVOS §5): " + ", ".join(nombres)
            escribir(ty, leer(ty).rstrip("\n") + "\najeno:\n- ruta: 06_RECURSOS/vendor/\n  descripcion: " + yaml_comillas(desc) + "\n")
            log(f"  temario.yml de {c.name}: clave `ajeno` añadida")
    # sílabo del seminario: clase yaac (Christophe Roger, LPPL) y sus fuentes Source Sans Pro
    syl = AREAS / "Academic_Class-Metodologia-investigacion" / "course_03_seminario-de-investigacion" / "00_ADMINISTRACION" / "syllabus"
    if (syl / "yaac-luatex.cls").exists():
        for n in ("yaac-luatex.cls", "yaac-xelatex.cls"):
            mover(syl / n, syl / "vendor" / n)
        if (syl / "fonts").is_dir():
            mover(syl / "fonts", syl / "vendor" / "fonts")
        tex = syl / "syllabus.tex"
        escribir(tex, re.sub(r"\\documentclass(\[[^]]*\])?\{yaac-luatex\}", r"\\documentclass\1{vendor/yaac-luatex}", leer(tex)))
        log("  syllabus.tex: \\documentclass{vendor/yaac-luatex}")
        for n in ("yaac-luatex.cls", "yaac-xelatex.cls"):
            p = (syl / "vendor" / n) if BIT["aplicar"] else (syl / n)
            escribir(p, leer(p).replace("Path = fonts/", "Path = vendor/fonts/"))
        log("  yaac-*.cls: Path = vendor/fonts/")
    # tema beamer «wue» huérfano (la presentación que lo usaba ya no existe; quedan sus auxiliares)
    wue = AREAS / "Academic_Class-Gestion-empresarial" / "03_temas" / "sesiones" / "presentacion" / "wue.sty"
    if wue.exists():
        mover(wue, wue.parent / "vendor" / "wue.sty")


def yaml_comillas(s: str) -> str:
    return '"' + s.replace('"', "'") + '"'


# --- artefactos --------------------------------------------------------------
GITIGNORE_AREA = """# Sistema / editores
.directory
.DS_Store
# Auxiliares LaTeX (artefactos de construcción: nunca se versionan, NORMATIVA_ARCHIVOS §5)
*.aux
*.log
*.nav
*.snm
*.toc
*.out
*.vrb
*.synctex.gz
*.fls
*.fdb_latexmk
*.bbl
*.blg
*.bcf
*.run.xml
*.lof
*.lot
# Jupyter
.ipynb_checkpoints/
# Stata / SPSS temporales
*.smcl
"""
PATRONES_GITIGNORE = ["*.aux", "*.log", "*.nav", "*.snm", "*.toc", "*.out", "*.vrb", "*.synctex.gz", "*.fls",
                      "*.fdb_latexmk", "*.bbl", "*.blg", "*.bcf", "*.run.xml", "*.lof", "*.lot", ".ipynb_checkpoints/"]


def es_artefacto(p: Path) -> bool:
    if p.name.endswith(".synctex.gz") or p.name.endswith(".run.xml"):
        return True
    if p.suffix.lower() == ".log":
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                return f.readline().startswith("This is ")
        except OSError:
            return False
    return p.suffix.lower() in val.ARTEFACTOS - {".log"}


def cmd_artefactos():
    log("== artefactos")
    raices = [*areas(), FW / "templates", FW / "scaffolds", FW / "examples", FW / "docs"]
    n = 0
    for raiz in raices:
        if not raiz.is_dir():
            continue
        for p in recorrer(raiz, SALTAR_DIRS - {"vendor"}):
            partes = p.relative_to(raiz).parts[:-1]
            if es_artefacto(p) or ".ipynb_checkpoints" in partes:
                borrar(p)
                n += 1
        for d in sorted(raiz.rglob(".ipynb_checkpoints")):
            if d.is_dir() and BIT["aplicar"] and not any(d.iterdir()):
                d.rmdir()
    log(f"  artefactos: {n}")
    for a in areas():
        gi = a / ".gitignore"
        if not gi.exists():
            log(f"  .gitignore nuevo: {a.name}")
            escribir(gi, GITIGNORE_AREA, nuevo=True)
            continue
        t = leer(gi)
        faltan = [x for x in PATRONES_GITIGNORE if not re.search(rf"^{re.escape(x)}\s*$", t, re.M)]
        if faltan:
            log(f"  .gitignore {a.name}: + {' '.join(faltan)}")
            escribir(gi, t.rstrip("\n") + "\n# Artefactos de construcción (NORMATIVA_ARCHIVOS §5)\n" + "\n".join(faltan) + "\n")


# --- cursos ------------------------------------------------------------------
def plan_cursos() -> list[tuple[Path, Path]]:
    plan = []
    for a in areas():
        fuera = sorted(c for c in a.glob("course_*") if c.is_dir() and not re.match(r"^course_\d\d_", c.name))
        usados = {int(m.group(1)) for c in a.glob("course_*") if (m := re.match(r"^course_(\d\d)", c.name))}
        orden = ORDEN_SIN_NN.get(a.name, [])
        fuera.sort(key=lambda c: (orden.index(c.name) if c.name in orden else 99, c.name))
        for c in fuera:
            m = re.match(r"^course_(\d\d)[-_]", c.name)
            if m:
                nn = int(m.group(1))
            else:
                nn = next(i for i in range(1, 100) if i not in usados)
                usados.add(nn)
            slug = snake(id_curso(c))
            plan.append((c, a / f"course_{nn:02d}_{slug}"))
    return plan


def cmd_cursos():
    log("== cursos fuera de patrón → course_NN_<slug>")
    plan = plan_cursos()
    seds = []
    for viejo, nuevo in plan:
        mover(viejo, nuevo)
        a = viejo.parent
        rd = a / "README.md"
        if rd.exists() and viejo.name in leer(rd):
            escribir(rd, leer(rd).replace(viejo.name, nuevo.name))
            log(f"      README de {a.name}: {viejo.name} → {nuevo.name}")
        seds.append(f"s|{a.name}/{viejo.name}/|{a.name}/{nuevo.name}/|g")
    if seds:
        log("  Para los repos que no toca esta herramienta (04 index, prompts, 01 notes):")
        log("    sed -i -e '" + "' -e '".join(seds) + "' <archivos>")
    return plan


# --- nombres -----------------------------------------------------------------
ESPECIALES = {"metadata pdf.lua": "metadata.pdf.lua",      # KOReader espera metadata.pdf.lua (el espacio lo puso un renombre masivo)
              "MIGRACION_LUALATEX.md": "MIGRACION_LUALATEX.md"}   # documento de raíz en mayúsculas (convención del ecosistema, §4)


def nuevo_nombre(p: Path) -> str | None:
    n = p.name
    if n in ESPECIALES:
        return ESPECIALES[n]
    if n in val.NOMBRES_AJENOS or n.startswith((".", "_")) or p.suffix.lower() in val.EXT_AJENAS:
        return None
    if val.MAYUSCULAS.match(n) and (p.parent == repo_de(p) or p.parent.name in ("meta", "docs")):
        return None
    if nombre_ok(n) or p.suffix.lower() in val.BINARIOS or es_artefacto(p):
        return None
    if nombre_ok(n.lower()):                       # el cambio mínimo: solo minúsculas (2012_EA.tex → 2012_ea.tex)
        return n.lower()
    return kebab(n) if p.suffix.lower() in (".md", ".tex", ".qmd") else snake(n)


def cmd_nombres():
    log("== nombres de archivo fuera de norma (sin las notas de 02_CONTENIDO)")
    raices = [*areas(), FW]
    hechos = 0
    for raiz in raices:
        for p in recorrer(raiz):
            if raiz == FW and p.relative_to(FW).parts[0] == "areas":
                continue
            if "02_CONTENIDO" in p.parts and p.suffix.lower() == ".md":
                continue
            nn = nuevo_nombre(p)
            if not nn:
                continue
            dst = p.with_name(nn)
            if dst.exists() and dst != p:
                log(f"  !! colisión: {rel_repo(p)} → {nn} ya existe; no se toca")
                continue
            mover(p, dst)
            hechos += 1
            if p.suffix.lower() in (".tex", ".qmd"):        # el PDF hermano sigue el nombre de su fuente
                pdf = p.with_suffix(".pdf")
                if pdf.exists():
                    mover(pdf, dst.with_suffix(".pdf"))
            area = raiz if raiz != FW else FW
            reemplazar_en_textos(area, p.name, nn, excluir={p, dst})
    log(f"  renombrados: {hechos}")


# --- registros: metadata.yml y temario.yml -----------------------------------
def sesiones(curso: Path):
    return sorted(s for s in (curso / "03_SESIONES").glob("S[0-9]*") if s.is_dir()) if (curso / "03_SESIONES").is_dir() else []


def migrar_metadata(meta: Path, curso: Path) -> str:
    t = leer(meta)
    lineas = t.split("\n")
    m = re.match(r"^S(\d\d)", meta.parent.name)
    nn = m.group(1) if m else "??"
    ident = f"# {rel_repo(meta)} — registro de la sesión {nn} de {id_curso(curso)}"
    # cabecera: la caja del scaffold (3 líneas) o nada
    if len(lineas) >= 3 and lineas[0].startswith("# ===") and lineas[1].startswith("# metadata.yml") and lineas[2].startswith("# ==="):
        lineas = [ident] + lineas[3:]
    elif not lineas[0].startswith("# ") or " — " not in lineas[0]:
        lineas = [ident] + lineas
    else:
        lineas[0] = ident
    slug = yaml_escalar(t, "slug") or yaml_escalar(t, "id") or re.sub(r"^S\d\d_?", "", meta.parent.name) or f"sesion_{nn}"
    out, tiene_estado, tiene_id, idx_titulo = [], False, False, None
    for l in lineas:
        if re.match(r"^numero:", l):
            if not tiene_id:
                out.append(f"id: {slug}"); tiene_id = True
            continue
        if re.match(r"^slug:", l):
            if not tiene_id:
                out.append(f"id: {slug}"); tiene_id = True
            continue
        if re.match(r"^id:", l):
            if tiene_id:
                continue
            tiene_id = True
        me = re.match(r"^estado:\s*([^\s#]*)(.*)$", l)
        if me:
            v = me.group(1)
            v2 = ESTADO_SESION.get(v, v)
            com = me.group(2)
            if "en_preparacion" in com or "impartida" in com:
                com = "       # borrador | activo | hecho (NORMATIVA_ARCHIVOS §2.1)"
            l = f"estado: {v2}{com}"
            tiene_estado = True
        if re.match(r"^titulo:", l):
            idx_titulo = len(out)
        out.append(l)
    if not tiene_id:
        out.insert(1, f"id: {slug}")
    if not tiene_estado:
        pos = (idx_titulo + 1) if idx_titulo is not None else 2
        out.insert(pos, "estado: borrador")
    return "\n".join(out)


def estado_curso(curso: Path, temario_txt: str) -> str:
    md = re.search(r"^dictados:\s*(.*)$", temario_txt, re.M)
    if md and md.group(1).strip() not in ("[]", "", "null"):
        return "activo"
    if re.search(r"^dictados:\s*$\n(?:- .+\n)+", temario_txt, re.M):
        return "activo"
    for s in sesiones(curso):
        mt = s / "metadata.yml"
        if mt.exists():
            v = yaml_escalar(leer(mt), "estado")
            if ESTADO_SESION.get(v, v) == "hecho":
                return "activo"
    return "borrador"


def migrar_temario(ty: Path, curso: Path) -> str:
    t = leer(ty)
    cid = yaml_escalar(t, "id") or yaml_escalar(t, "curso") or curso.name
    lineas = t.split("\n")
    cab = [f"# {rel_repo(ty)} — registro del curso {cid}: fuente única del currículo (unidades, temas, recursos)",
           "# Se editan aquí unidades, temas y recursos; README, esqueletos de 02_CONTENIDO, ficha web,",
           "# temario del learning-skill y checklist de estudio se GENERAN con: 10 Class/scripts/temario-generar.sh"]
    i = 0
    while i < len(lineas) and lineas[i].startswith("#"):
        i += 1
    cuerpo = lineas[i:]
    out, tiene_estado = [], False
    for l in cuerpo:
        if re.match(r"^curso:", l):
            l = "id:" + l[len("curso:"):]
        if re.match(r"^estado:", l):
            tiene_estado = True
        out.append(l)
    if not tiene_estado:
        for k, l in enumerate(out):
            if re.match(r"^titulo:", l):
                out.insert(k + 1, f"estado: {estado_curso(curso, t)}")
                break
        else:
            out.insert(0, f"estado: {estado_curso(curso, t)}")
    return "\n".join(cab + out)


def cmd_registros():
    log("== registros: metadata.yml (sesión) y temario.yml (curso)")
    nm = nt = 0
    for c in cursos():
        ty = c / "temario.yml"
        if ty.exists():
            nuevo = migrar_temario(ty, c)
            if nuevo != leer(ty):
                escribir(ty, nuevo); nt += 1
        for s in sesiones(c):
            mt = s / "metadata.yml"
            if mt.exists():
                nuevo = migrar_metadata(mt, c)
                if nuevo != leer(mt):
                    escribir(mt, nuevo); nm += 1
    log(f"  temario.yml: {nt} · metadata.yml: {nm}")


# --- cabeceras (identidad en la línea 1) --------------------------------------
def limpiar_tex(s: str) -> str:
    s = re.sub(r"\\\\|\\newline", " ", s)
    s = re.sub(r"\\[A-Za-z@]+\*?(\[[^]]*\])?", "", s)
    s = s.replace("{", "").replace("}", "").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


def que_es_tex(p: Path, texto: str) -> str:
    partes = p.parts
    m = re.search(r"\\title(?:\[[^]]*\])?\{((?:[^{}]|\{[^{}]*\})*)\}", texto)
    titulo = limpiar_tex(m.group(1)) if m else ""
    if "02_Clase" in partes:
        ses = p.parents[1] if p.parent.name == "02_Clase" else p.parents[2]
        mt = ses / "metadata.yml"
        nn = re.match(r"^S(\d\d)", ses.name)
        tit = (yaml_escalar(leer(mt), "titulo") if mt.exists() else None) or titulo or ses.name
        clase = "deck" if p.stem in ("slides", "index", "clase", "diapositivas", "main") else "material de clase"
        return f"{clase} de la sesión {nn.group(1) if nn else '??'}: {tit}"
    if titulo:
        return titulo.replace(" — ", ": ")
    cab = texto.split("\\documentclass", 1)[0] if "\\documentclass" in texto[:3000] else texto
    for l in cab.splitlines()[:15]:
        c = l.strip()
        if c.startswith("%") and re.search(r"[A-Za-zÁÉÍÓÚáéíóúñ]{3,}", c) and not re.match(r"^%+\s*[=\-]{3,}", c) and "!TEX" not in c:
            return re.sub(r"^%+\s*", "", c).replace(" — ", ": ").rstrip(".")
    if p.stem in ("syllabus", "silabo"):
        return "sílabo del curso"
    ctx = {"04_EVALUACIONES": "evaluación", "06_RECURSOS": "recurso LaTeX", "00_ADMINISTRACION": "documento administrativo",
           "01_PLANIFICACION": "documento de planificación", "08_INVESTIGACION": "documento de investigación"}
    for k, v in ctx.items():
        if k in partes:
            return f"{v}: {p.stem.replace('_', ' ').replace('-', ' ')}"
    return f"documento LaTeX: {p.stem.replace('_', ' ').replace('-', ' ')}"


def que_es_comentario(texto: str, marca: str) -> str | None:
    lineas = texto.splitlines()[:25]
    for l in lineas:                       # una línea «Sesión N. Tema» describe mejor que «Curso: …»
        c = l.strip()
        if c.startswith(marca) and re.search(r"Sesi[oó]n\s*\d", c):
            return re.sub(rf"^{re.escape(marca)}+\s*", "", c).replace(" — ", ": ").rstrip(".")
    for l in lineas:
        c = l.strip()
        if c.startswith(marca) and re.search(r"[A-Za-zÁÉÍÓÚáéíóúñ]{3,}", c) and not re.match(rf"^{re.escape(marca)}+\s*[=\-#*]{{3,}}", c) \
                and "coding" not in c and "!/" not in c:
            return re.sub(rf"^{re.escape(marca)}+\s*", "", c).replace(" — ", ": ").rstrip(".")
    return None


def minusculas_gritadas(s: str) -> str:
    """Palabras enteramente en mayúsculas → minúsculas; las mixtas (CampusTeX) se conservan."""
    return " ".join(w.lower() if re.fullmatch(r"[A-ZÁÉÍÓÚÑ0-9/().,:;·\-]{2,}", w) else w for w in s.split(" "))


def cabecera_plantilla(p: Path, texto: str) -> str | None:
    """Plantillas del framework: `% PLANTILLA — X` → identidad; `Compilar:` → `Uso:`."""
    lineas = texto.split("\n")
    for i, l in enumerate(lineas[:4]):
        m = re.match(r"^%\s*PLANTILLA(?:\s+\d+)?\s*[—-]+\s*(.+)$", l)
        if m:
            que = "plantilla: " + minusculas_gritadas(m.group(1).strip())
            lineas[i] = f"% {rel_repo(p)} — {que}"
            break
    else:
        return None
    for i, l in enumerate(lineas[:12]):
        mc = re.match(r"^(%\s*)Compilar:\s*(.*)$", l)
        if mc:
            lineas[i] = f"{mc.group(1)}Uso: scripts/build.sh {p.name}   (LuaLaTeX)"
    return "\n".join(lineas)


def cabecera_scaffold_slides(p: Path, texto: str) -> str:
    lineas = texto.split("\n")
    ident = "% {{RUTA_SESION}}/02_Clase/slides.tex — deck Beamer de la sesión {{NUMBER}}: {{TITLE}}"
    ini = 1 if lineas[0].startswith("%!TEX") else 0
    lineas.insert(ini, ident)
    for i, l in enumerate(lineas[:12]):
        mc = re.match(r"^(%\s*)Compilar:\s*(.*)$", l)
        if mc:
            lineas[i] = f"{mc.group(1)}Uso: {mc.group(2)}"
    return "\n".join(lineas)


def cmd_cabeceras():
    log("== identidad en la línea 1 (código propio sin ella)")
    n = 0
    raices = [*areas(), FW]
    for raiz in raices:
        for p in recorrer(raiz):
            if raiz == FW and p.relative_to(FW).parts[0] == "areas":
                continue
            fam = val.familia(p)
            if fam not in ("latex", "python", "bash", "yaml", "bib", "quarto"):
                continue
            if p.name in ("metadata.yml", "temario.yml", "dictado.yml"):
                continue
            lineas = val.leer(p)
            texto = leer(p)
            decl, desc = val.identidad(fam, lineas, texto, nombre_suite=p.parent.name)
            if decl is not None or desc is not None:
                continue
            rel = rel_repo(p)
            nuevo = None
            if fam == "latex":
                if raiz == FW and p.relative_to(FW).parts[0] == "templates":
                    nuevo = cabecera_plantilla(p, texto)
                elif raiz == FW and rel == "scaffolds/session/02_Clase/slides.tex":
                    nuevo = cabecera_scaffold_slides(p, texto)
                if nuevo is None:
                    que = que_es_tex(p, texto)
                    ini = 1 if texto.startswith("%!TEX") else 0
                    ls = texto.split("\n")
                    ls.insert(ini, f"%% {rel} — {que}")
                    nuevo = "\n".join(ls)
            elif fam == "python":
                que = que_es_comentario(texto, "#") or f"código de {p.parent.name}: {p.stem.replace('_', ' ')}"
                ls = texto.split("\n")
                ini = 0
                while ini < len(ls) and (ls[ini].startswith("#!") or "coding" in ls[ini][:30] and ls[ini].startswith("#")):
                    ini += 1
                ls.insert(ini, f'"""{rel} — {que}."""')
                nuevo = "\n".join(ls)
            elif fam == "bash":
                que = que_es_comentario(texto, "#") or p.stem.replace("_", " ")
                ls = texto.split("\n")
                ini = 1 if ls and ls[0].startswith("#!") else 0
                ls.insert(ini, f"# {rel} — {que}")
                nuevo = "\n".join(ls)
            elif fam == "yaml":
                que = que_es_comentario(texto, "#") or p.stem.replace("_", " ")
                nuevo = f"# {rel} — {que}\n" + texto
            elif fam == "bib":
                nuevo = f"% {rel} — bibliografía de {p.parent.name.replace('_', ' ')}; claves apellidoAAAApalabra; a mano\n" + texto
            elif fam == "quarto":
                if not texto.strip():
                    nuevo = f'---\ntitle: "Recursos de {p.parents[1].name}"\n---\n'
                else:
                    continue
            if nuevo is not None and nuevo != texto:
                log(f"  id  {rel}")
                escribir(p, nuevo)
                n += 1
    log(f"  cabeceras añadidas: {n}")


# --- frontmatter de Markdown suelto -----------------------------------------
GENERADO_PUB = "<!-- GENERADO por 10 Class/scripts/publish-session.sh al publicar la sesión; no editar -->"


def titulo_h1(texto: str, p: Path) -> str:
    m = re.search(r"^#\s+(.+)$", texto, re.M)
    t = m.group(1).strip() if m else p.stem.replace("_", " ").replace("-", " ")
    t = re.sub(r"^[^\w{]+", "", t).strip()             # emojis y adornos delante del título
    return t.replace('"', "'")


def con_frontmatter(p: Path, texto: str) -> str | None:
    lineas = texto.split("\n")
    estado = "borrador" if p.name in ("retrospective.md",) else "activo"
    if lineas and lineas[0].strip() == "---":
        fm = val.frontmatter(lineas)
        if fm is None or "tipo" in fm or "type" in fm:
            return None
        ins = ["tipo: doc"]
        if "estado" not in fm:
            ins.append(f"estado: {estado}")
        return "\n".join([lineas[0], *ins, *lineas[1:]])
    cab = ["---", "tipo: doc", f'titulo: "{titulo_h1(texto, p)}"', f"estado: {estado}", "---"]
    if p.name == "_PUBLICADO.md":
        cab.append(GENERADO_PUB)
    return "\n".join(cab) + "\n" + texto


def cmd_frontmatter():
    log("== frontmatter con `tipo` en Markdown suelto (fuera de 02_CONTENIDO)")
    n = 0
    for raiz in [*areas(), FW]:
        for p in recorrer(raiz):
            if raiz == FW and p.relative_to(FW).parts[0] == "areas":
                continue
            if p.suffix.lower() != ".md" or p.name in EXENTOS_MD or p.name.endswith(".html.md"):
                continue
            if "02_CONTENIDO" in p.parts:
                continue
            nuevo = con_frontmatter(p, leer(p))
            if nuevo is not None:
                log(f"  fm  {rel_repo(p)}")
                escribir(p, nuevo)
                n += 1
    log(f"  frontmatter añadido: {n}")


def cmd_todo():
    cmd_vendor()
    cmd_artefactos()
    cmd_cursos()
    cmd_nombres()
    cmd_registros()
    cmd_cabeceras()
    cmd_frontmatter()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["vendor", "artefactos", "cursos", "nombres", "registros", "cabeceras", "frontmatter", "todo"])
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--bitacora", help="carpeta donde anotar renombres/borrados/modificados (para el UNDO)")
    a = ap.parse_args()
    BIT["aplicar"] = a.aplicar
    BIT["dir"] = a.bitacora
    if a.bitacora:
        Path(a.bitacora).mkdir(parents=True, exist_ok=True)
    {"vendor": cmd_vendor, "artefactos": cmd_artefactos, "cursos": cmd_cursos, "nombres": cmd_nombres,
     "registros": cmd_registros, "cabeceras": cmd_cabeceras, "frontmatter": cmd_frontmatter, "todo": cmd_todo}[a.accion]()
    if a.bitacora and not a.aplicar:
        (Path(a.bitacora) / f"plan_{a.accion}.tsv").write_text("\n".join(BIT["plan"]) + "\n", encoding="utf-8")
    print("\n" + ("APLICADO" if a.aplicar else "SIMULACIÓN (usa --aplicar)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
