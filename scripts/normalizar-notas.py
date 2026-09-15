#!/usr/bin/env python3
"""scripts/normalizar-notas.py — las notas de estudio de `02_CONTENIDO/**/*.md` al régimen del vault.

Objetivo: que cada apunte de un curso se llame en kebab-case (`1 1 curso 0.md` →
  `1-1-curso-0.md`) y lleve el frontmatter único (`tipo: apunte`, `titulo`, `estado`,
  `tags`), sin perder ningún enlace: los wikilinks, los enlaces Markdown relativos y
  los `archivo:` de cada `temario.yml` se reescriben con el nombre nuevo.
Método: recorre `areas/*/course_*/02_CONTENIDO/**/*.md` (salvo README.md), calcula el
  nombre kebab y el frontmatter nuevo conservando todas las claves que ya hubiera,
  renombra con `git mv` cuando el archivo está versionado y sustituye las referencias
  en todos los `.md` y `temario.yml` de las áreas. Simula por defecto.
Fundamento: meta/NORMATIVA_ARCHIVOS.md §4 (nombres), §6.2 (Markdown), §10.4 (las notas
  de estudio de 10 Class son régimen del vault); encargo M7 (2026-09-15) punto 4.
Alternativa: renombrar con `rename` y arreglar enlaces a mano. Se descarta: 2 000
  archivos y 63 wikilinks + 9 enlaces relativos + 1 700 `archivo:` que se romperían.
Límite: no toca notas fuera de `02_CONTENIDO` ni referencias en otros repos
  (`01 notes`, `prompts`): las imprime como `sed` para el informe.

Uso:
  python3 scripts/normalizar-notas.py [--aplicar] [--bitacora DIR] [CURSO_DIR ...]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from pathlib import Path

FW = Path(__file__).resolve().parents[1]
AREAS = FW / "areas"
SALTAR = {".git", "_ESTANDARIZACION", "vendor", "_POR_REVISAR", "build", "data", "code", "legacy", "archive", "archivo", "registro", "logs", "originales", "respaldos", "backup", "backups"}
ESTADO_MAP = {"completada": "hecho", "impartida": "hecho", "migrada": "borrador", "en_preparacion": "borrador",
              "en curso": "activo", "en-curso": "activo", "planeada": "borrador"}
ESTADOS = {"bandeja", "borrador", "activo", "en_espera", "hecho", "archivado", "retirado"}

BIT = {"dir": None, "aplicar": False, "plan": []}


def bitacora(clase, *campos):
    if BIT["dir"] is None:
        return
    if not BIT["aplicar"]:
        BIT["plan"].append("\t".join([clase, *campos])); return
    nombre = {"mv": "renombres.tsv", "mod": "modificados.txt"}[clase]
    with open(Path(BIT["dir"]) / nombre, "a", encoding="utf-8") as f:
        f.write("\t".join(campos) + "\n")


def repo_de(p: Path) -> Path:
    for a in [p, *p.parents]:
        if (a / ".git").exists():
            return a
    return FW


def tracked(p: Path) -> bool:
    repo = repo_de(p)
    return subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", str(p.relative_to(repo))],
                          capture_output=True, text=True).returncode == 0


def kebab(nombre: str) -> str:
    base, _, ext = nombre.rpartition(".")
    if not base:
        base, ext = ext, ""
    b = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode().lower()
    b = re.sub(r"[^a-z0-9]+", "-", b).strip("-")
    return f"{b}.{ext.lower()}" if ext else b


def recorrer_md(raiz: Path):
    for p in sorted(raiz.rglob("*.md")):
        if any(x in SALTAR or x.startswith("_backup") for x in p.relative_to(raiz).parts[:-1]):
            continue
        yield p


def notas(cursos: list[Path]):
    for c in cursos:
        cont = c / "02_CONTENIDO"
        if cont.is_dir():
            for p in recorrer_md(cont):
                if p.name != "README.md":
                    yield p


def titulo_de(texto: str, p: Path, fm: dict[str, str]) -> str:
    if fm.get("title"):
        return fm["title"]
    if fm.get("titulo"):
        return fm["titulo"]
    m = re.search(r"^#\s+(.+)$", texto, re.M)
    t = m.group(1).strip() if m else re.sub(r"^\d+(-\d+)?-", "", kebab(p.name)[:-3]).replace("-", " ")
    t = re.sub(r"^[^\w]+", "", t).strip()
    return '"' + t.replace('"', "'") + '"'


def frontmatter_nuevo(texto: str, p: Path) -> str:
    lineas = texto.split("\n")
    if lineas and lineas[0].strip() == "---":
        fin = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
        if fin is not None:
            bloque, resto = lineas[1:fin], lineas[fin + 1:]
            fm = {}
            for l in bloque:
                m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", l)
                if m:
                    fm[m.group(1)] = m.group(2).strip()
            out = ["tipo: apunte"]
            if "titulo" not in fm:
                out.append(f"titulo: {titulo_de(texto, p, fm)}")
            estado = fm.get("estado", "").strip("'\"")
            if not estado:
                out.append("estado: activo")
            for l in bloque:
                m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", l)
                if m and m.group(1) in ("title", "tipo"):
                    continue
                if m and m.group(1) == "estado":
                    v = m.group(2).strip().strip("'\"")
                    l = f"estado: {ESTADO_MAP.get(v, v if v in ESTADOS else 'activo')}"
                out.append(l)
            return "\n".join(["---", *out, "---", *resto])
    return "\n".join(["---", "tipo: apunte", f"titulo: {titulo_de(texto, p, {})}", "estado: activo", "---", *lineas])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cursos", nargs="*")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--bitacora")
    a = ap.parse_args()
    BIT["aplicar"], BIT["dir"] = a.aplicar, a.bitacora
    if a.bitacora:
        Path(a.bitacora).mkdir(parents=True, exist_ok=True)
    cursos = [Path(c).resolve() for c in a.cursos] or sorted(c for c in AREAS.glob("Academic_Class-*/course_*") if c.is_dir())

    # 1) plan de renombres y frontmatter
    renombres: dict[Path, Path] = {}
    contenido: dict[Path, str] = {}
    for p in notas(cursos):
        texto = p.read_text(encoding="utf-8", errors="replace")
        nuevo = frontmatter_nuevo(texto, p)
        if nuevo != texto:
            contenido[p] = nuevo
        nn = kebab(p.name)
        if nn != p.name:
            dst = p.with_name(nn)
            if dst.exists():
                print(f"  !! colisión: {p} → {nn} ya existe; no se renombra")
                continue
            renombres[p] = dst
    print(f"notas: {sum(1 for _ in notas(cursos))} · con frontmatter nuevo: {len(contenido)} · a renombrar: {len(renombres)}")

    # 2) referencias: wikilinks por nombre base, enlaces Markdown relativos y `archivo:` de temario.yml
    por_base = {p.name[:-3]: renombres[p].name[:-3] for p in renombres}
    por_nombre = {p.name: renombres[p].name for p in renombres}
    tocados = 0
    objetivos = [q for aa in sorted(AREAS.glob("Academic_Class-*")) for q in recorrer_md(aa)]
    objetivos += [t for aa in sorted(AREAS.glob("Academic_Class-*")) for t in aa.glob("course_*/temario.yml")]
    seds = []
    for q in objetivos:
        t = contenido.get(q) or q.read_text(encoding="utf-8", errors="replace")
        orig = t
        if q.suffix == ".md":
            def wl(m):
                base = m.group(1).strip()
                return f"[[{por_base[base]}{m.group(2)}" if base in por_base else m.group(0)
            t = re.sub(r"\[\[([^\]|#]+)([\]|#])", wl, t)
            def ml(m):
                ruta = m.group(2)
                dec = urllib.parse.unquote(ruta)
                nombre = dec.rsplit("/", 1)[-1]
                if nombre in por_nombre:
                    nueva = dec[: len(dec) - len(nombre)] + por_nombre[nombre]
                    return f"{m.group(1)}({nueva})"
                return m.group(0)
            def ml_ang(m):                          # forma `(<ruta con espacios.md>)`
                dec = m.group(2)
                nombre = dec.rsplit("/", 1)[-1]
                if nombre in por_nombre:
                    return f"{m.group(1)}<{dec[: len(dec) - len(nombre)] + por_nombre[nombre]}>)"
                return m.group(0)
            t = re.sub(r"(\]\()<([^>]+\.md)>\)", ml_ang, t)
            t = re.sub(r"(\]\()([^)<>\s]+\.md)\)", ml, t)
        else:
            for viejo, nuevo in por_nombre.items():
                t = t.replace("/" + viejo, "/" + nuevo)
        if t != orig:
            contenido[q] = t
            tocados += 1
    print(f"archivos con referencias reescritas: {tocados}")
    # referencias fuera de las áreas (otros repos): solo se informan
    for viejo, nuevo in por_nombre.items():
        seds.append((viejo, nuevo))

    # 3) aplicar: primero contenido (sobre la ruta vieja), luego renombres
    for p, t in sorted(contenido.items()):
        bitacora("mod", str(p))
        if a.aplicar:
            p.write_text(t, encoding="utf-8")
    for p, dst in sorted(renombres.items()):
        bitacora("mv", str(p), str(dst))
        if a.aplicar:
            if tracked(p):
                subprocess.run(["git", "-C", str(repo_de(p)), "mv", "-k", str(p), str(dst)], check=True)
                if p.exists():
                    os.rename(p, dst)
            else:
                os.rename(p, dst)
    if a.bitacora and not a.aplicar:
        (Path(a.bitacora) / "plan_notas.tsv").write_text("\n".join(BIT["plan"]) + "\n", encoding="utf-8")
        (Path(a.bitacora) / "notas_renombres.tsv").write_text("".join(f"{v}\t{n}\n" for v, n in seds), encoding="utf-8")
    print("APLICADO" if a.aplicar else "SIMULACIÓN (usa --aplicar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
