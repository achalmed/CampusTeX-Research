#!/usr/bin/env python3
"""
publicar-web.py — Publica un DICTADO en la web del hub por HARDLINK (F5.2, 2026-09-06; modelo §4.4 desde M5, 2026-09-15).

  publicar-web.py DICTADO [--aplicar]         DICTADO: clave o ruta de docencia/dictados/<clave>

Lee docencia/dictados/<clave>/dictado.yml:

  web: {materia: metodologia-de-la-investigacion, edicion: 2026-1-cau-unsch}
  sesiones:
    - {orden: 1, curso: monografias, sesion: s01-la-monografia, web: session_01_la_monografia}

Para cada sesión toma su módulo `publicacion/<web>/` (creado por publish-session.sh) y en
`04 index/cursos/<web.materia>/<web.edicion>/<web>/`:
  · slides/ evaluation/ practice/ homework/ → cada archivo pasa a ser un HARDLINK del módulo
    (si la web tenía una copia, se sustituye por el enlace: un solo inodo, dos canales);
  · index.qmd y resources/_links.md se CREAN si faltan (desde sesion.yml de la sesión) y nunca se sobrescriben;
  · la portada de la edición (index.qmd) se crea si falta.
Un dictado `legado: true` no se publica (sus fuentes no están en el framework). Sin --aplicar es simulación.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

import yaml

FW = Path(__file__).resolve().parents[1]
DOCS = FW.parent
WEB_CURSOS = DOCS / "04 index" / "cursos"
SUBS = ("slides", "evaluation", "practice", "homework")
IGNORAR = {".gitkeep", "_PUBLICADO.md", "index.md", "README.md"}


def leer_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def frontmatter_title(qmd: Path) -> str | None:
    if not qmd.exists():
        return None
    m = re.search(r'^title:\s*"?(.+?)"?\s*$', qmd.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


DOCENCIA = FW / "docencia"


def dictado_dir(arg: str) -> Path | None:
    for cand in (Path(arg), DOCENCIA / "dictados" / arg):
        if (cand / "dictado.yml").exists():
            return cand.resolve()
    return None


def modulo_de(dictado: Path, web: str) -> Path | None:
    p = dictado / "publicacion" / web
    return p if p.is_dir() else None


def sesion_de(curso: str, sesion: str) -> Path | None:
    p = DOCENCIA / "cursos" / curso / "03-sesiones" / sesion
    return p if p.is_dir() else None


def index_qmd_sesion(meta: dict, orden: int, web_curso_titulo: str, edicion: str, institucion: str, slides_pdf: str | None) -> str:
    titulo = meta.get("titulo") or f"Sesión {orden:02d}"
    fecha = meta.get("fecha") or dt.date.today().isoformat()
    out = ["---", f'title: "{titulo}"',
           f'description: "Sesión del curso {web_curso_titulo} ({edicion}, {institucion})."',
           f"date: {fecha}", f"order: {orden}", "categories: []", "image: /assets/img/default-preview.jpg", "---", ""]
    if slides_pdf:
        out += ["## Diapositivas", "", '::: {#fig-slides fig-cap="Diapositivas de la sesión"}', "```{=html}",
                f'<object data="slides/{slides_pdf}" type="application/pdf" width="100%" height="760"><p><a href="slides/{slides_pdf}">Descargar diapositivas (PDF)</a></p></object>',
                "```", ":::", ""]
    out += ["## Materiales", "", "{{< include resources/_links.md >}}", ""]
    return "\n".join(out)


def links_md(webdir: Path) -> str:
    out = ["### Descargas", ""]
    algo = False
    for sub, etiqueta in (("practice", "Práctica"), ("homework", "Tarea"), ("evaluation", "Evaluación")):
        files = sorted(f for f in (webdir / sub).glob("*") if f.is_file() and f.name not in IGNORAR)
        if files:
            algo = True
            out += [f"**{etiqueta}**", ""]
            out += [f"- [{f.name}](<{sub}/{f.name}>)" for f in files]
            out.append("")
    if not algo:
        out += ["_Materiales por publicar._", ""]
    out += ["### Enlaces", "", "<!-- - [Recurso externo](https://…) -->", ""]
    return "\n".join(out)


def index_qmd_edicion(web_curso_titulo: str, periodo_web: str, institucion: str, n: int, descripcion: str) -> str:
    return "\n".join([
        "---", f'title: "{web_curso_titulo} — {periodo_web} · {institucion}"', f'subtitle: "{n} sesiones · {institucion}"',
        f'description: "{descripcion}"', "categories: [Investigación]", "image: /assets/img/default-preview.jpg",
        "listing:", "  - id: sesiones", "    contents:", '      - "session_*/index.qmd"', "    type: default", '    sort: "order"',
        "    sort-ui: false", "    filter-ui: true", "    fields: [title, categories, date, image]", "    image-align: left", "    feed: true",
        "header-includes: |", '  <link rel="stylesheet" href="/assets/css/pages/listing.css">', '  <link rel="stylesheet" href="/assets/css/pages/courses.css">',
        "format:", "  html:", "    page-layout: full", "title-block-banner: false", "toc: false", "comments: false", "---", "",
        f"**Docente:** Edison Achalma · **Institución:** {institucion} · **Periodo:** {periodo_web} · **Sesiones:** {n}", "",
        "Cada sesión trae sus diapositivas y materiales (práctica, tareas, evaluación y recursos) descargables.", "",
        "## Sesiones", "", "::: {#sesiones}", ":::", ""])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dictado"); ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    aplicar = a.aplicar
    dictado = dictado_dir(a.dictado)
    if dictado is None:
        print(f"No es un dictado (falta dictado.yml): {a.dictado}"); return 3
    d = leer_yaml(dictado / "dictado.yml")
    if d.get("legado"):
        print(f"{dictado.name}: dictado legado (sin fuentes en el framework); la web conserva su copia. Nada que publicar."); return 0
    web = d["web"]; institucion = d.get("institucion", "")
    web_curso_dir = WEB_CURSOS / (web.get("materia") or web.get("curso"))
    if not web_curso_dir.is_dir():
        print(f"No existe la ficha web {web_curso_dir} (créala con temario-generar o desde _plantillas/curso.qmd)"); return 3
    titulo_web = frontmatter_title(web_curso_dir / "index.qmd") or web["curso"]
    edicion_dir = web_curso_dir / web["edicion"]
    periodo_web = web["edicion"].split("-cau")[0] if "-cau" in web["edicion"] else d.get("periodo", web["edicion"])
    enlaces = sustituidos = creados = huerfanos = 0
    faltan = []
    for s in sorted(d["sesiones"], key=lambda x: x["orden"]):
        mod = modulo_de(dictado, s["web"])
        if mod is None:
            faltan.append(f"{s['curso']} {s['sesion']}")
            print(f"  {s['web']:<40} SIN MÓDULO → ./scripts/publish-session.sh {dictado.name} {s['curso']} {s['sesion'][1:3]}")
            continue
        webdir = edicion_dir / s["web"]
        slides_pdf = None
        for sub in SUBS:
            src = mod / sub
            if not src.is_dir():
                continue
            dst = webdir / sub
            for f in sorted(src.iterdir()):
                if not f.is_file() or f.name in IGNORAR:
                    continue
                if sub == "slides" and f.suffix.lower() == ".pdf" and slides_pdf is None:
                    slides_pdf = f.name
                t = dst / f.name
                if t.exists():
                    if os.path.samefile(t, f):
                        enlaces += 1
                        continue
                    sustituidos += 1
                    if aplicar:
                        t.unlink(); os.link(f, t)
                else:
                    creados += 1
                    if aplicar:
                        dst.mkdir(parents=True, exist_ok=True); os.link(f, t)
            # archivos que la web tiene y el módulo no (copias huérfanas)
            if dst.is_dir():
                origen = {f.name for f in src.iterdir() if f.is_file()}
                for f in dst.iterdir():
                    if f.is_file() and f.name not in IGNORAR and f.name not in origen:
                        huerfanos += 1
                        print(f"  {s['web']:<40} huérfano en la web (no está en el módulo): {sub}/{f.name}")
        # páginas: solo si faltan
        ses = sesion_de(s["curso"], s["sesion"])
        meta = leer_yaml(ses / "sesion.yml") if ses and (ses / "sesion.yml").exists() else {}
        idx = webdir / "index.qmd"
        if not idx.exists():
            if aplicar:
                webdir.mkdir(parents=True, exist_ok=True)
                idx.write_text(index_qmd_sesion(meta, s["orden"], titulo_web, web["edicion"], institucion, slides_pdf), encoding="utf-8")
            print(f"  {s['web']:<40} index.qmd {'creado' if aplicar else 'se crearía'}")
        links = webdir / "resources" / "_links.md"
        if not links.exists():
            if aplicar:
                links.parent.mkdir(parents=True, exist_ok=True)
                (links.parent / "readings").mkdir(exist_ok=True)
                links.write_text(links_md(webdir), encoding="utf-8")
            print(f"  {s['web']:<40} resources/_links.md {'creado' if aplicar else 'se crearía'}")
        print(f"  {s['web']:<40} ← {s['curso']}/03-sesiones/{s['sesion']}  (módulo publicacion/{mod.name})")
    if not (edicion_dir / "index.qmd").exists():
        if aplicar:
            edicion_dir.mkdir(parents=True, exist_ok=True)
            (edicion_dir / "index.qmd").write_text(index_qmd_edicion(titulo_web, periodo_web, institucion, len(d["sesiones"]), d.get("descripcion", "")), encoding="utf-8")
        print(f"  portada de la edición {web['edicion']}: {'creada' if aplicar else 'se crearía'}")
    print(f"\n{'APLICADO' if aplicar else 'SIMULACIÓN'}: hardlinks ya correctos={enlaces} · copias sustituidas por hardlink={sustituidos} · enlaces nuevos={creados} · huérfanos en la web={huerfanos} · sesiones sin módulo={len(faltan)}")
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
