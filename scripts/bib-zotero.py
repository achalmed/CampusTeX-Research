#!/usr/bin/env python3
"""scripts/bib-zotero.py — el referencias.bib de un documento, generado desde Zotero (APA 7 con biblatex-apa).

Objetivo: que un examen, una práctica o un informe del framework cite en APA con las claves de Better BibTeX de
  Zotero, la autoridad de citas del ecosistema (biblioteca-studio/docs/citar.md), aunque todavía no exista la
  exportación automática `zotero.bib` (ZOTERO_BIB de core/env.sh). Cuando exista, el documento puede pedir
  `\\addbibresource{zotero.bib}` y este archivo sobra.
Método: 1) las claves citadas salen del .tex (`\\cite`, `\\textcite`, `\\parencite`, `\\citeauthor`… con o sin
  argumentos opcionales); 2) cada clave se busca en Zotero por el campo `citationKey` que fija Better BibTeX, leyendo
  `zotero.sqlite` en modo inmutable (nunca se escribe ni se bloquea la base); 3) cada ítem se traduce a BibLaTeX
  (book, article, incollection, thesis, report, unpublished, online, misc) con sus creadores, título, fecha,
  editorial, lugar, edición, serie, revista, volumen, número, páginas, DOI y URL; 4) se escribe
  `<carpeta>/referencias.bib` con la marca GENERADO. Ningún código de Calibre entra en el .bib ni en el documento.
Uso:
    python3 scripts/bib-zotero.py ARCHIVO.tex            # simula: muestra el .bib y lo que falta
    python3 scripts/bib-zotero.py ARCHIVO.tex --aplicar  # escribe <carpeta>/referencias.bib
Salida: 0 si todas las claves están en Zotero; 1 si falta alguna (se lista; no se inventa); 2 sin Zotero.
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

CITA = re.compile(r"\\(?:[A-Za-z]*cite[A-Za-z]*|citeauthor|citeyear|nocite)\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]+)\}")
TIPOS = {"book": "book", "journalArticle": "article", "bookSection": "incollection", "thesis": "thesis",
         "report": "report", "manuscript": "unpublished", "webpage": "online", "presentation": "misc",
         "conferencePaper": "inproceedings", "magazineArticle": "article", "newspaperArticle": "article",
         "document": "misc", "statute": "legislation", "case": "jurisdiction"}
CAMPOS = {"title": "title", "publisher": "publisher", "place": "location", "edition": "edition", "series": "series",
          "publicationTitle": "journaltitle", "bookTitle": "booktitle", "volume": "volume", "issue": "number",
          "pages": "pages", "DOI": "doi", "url": "url", "university": "institution", "institution": "institution",
          "ISBN": "isbn", "shortTitle": "shorttitle"}
ROLES = {"author": "author", "editor": "editor", "translator": "translator", "bookAuthor": "bookauthor"}


def ruta_zotero() -> Path | None:
    env = Path(__file__).resolve().parents[2] / "core" / "env.sh"
    if os.environ.get("ZOTERO_DB"):
        return Path(os.environ["ZOTERO_DB"])
    if env.is_file():
        r = subprocess.run(["bash", "-c", 'source "$1" && printf "%s" "$ZOTERO_DB"', "_", str(env)],
                           capture_output=True, text=True)
        if r.stdout.strip():
            return Path(r.stdout.strip())
    return None


def claves_citadas(tex: Path) -> list[str]:
    texto = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in tex.read_text(encoding="utf-8").splitlines())
    vistas: list[str] = []
    for m in CITA.finditer(texto):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in vistas:
                vistas.append(k)
    return vistas


def _escapar(valor: str) -> str:
    return valor.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")


def entrada(con: sqlite3.Connection, clave: str) -> str | None:
    fila = con.execute("""select i.itemID, t.typeName from items i join itemTypes t on t.itemTypeID = i.itemTypeID
        join itemData d on d.itemID = i.itemID join fields f on f.fieldID = d.fieldID
        join itemDataValues v on v.valueID = d.valueID
        where f.fieldName = 'citationKey' and v.value = ? and i.itemID not in (select itemID from deletedItems)""",
                       (clave,)).fetchone()
    if fila is None:
        return None
    item, tipo = fila
    datos = dict(con.execute("""select f.fieldName, v.value from itemData d join fields f on f.fieldID = d.fieldID
        join itemDataValues v on v.valueID = d.valueID where d.itemID = ?""", (item,)).fetchall())
    creadores: dict[str, list[str]] = {}
    for apellido, nombre, modo, rol in con.execute("""select c.lastName, c.firstName, c.fieldMode, ct.creatorType
            from itemCreators ic join creators c on c.creatorID = ic.creatorID
            join creatorTypes ct on ct.creatorTypeID = ic.creatorTypeID where ic.itemID = ? order by ic.orderIndex""",
                                                   (item,)):
        campo = ROLES.get(rol, "author")
        persona = f"{{{apellido}}}" if modo == 1 or not nombre else f"{apellido}, {nombre}"
        creadores.setdefault(campo, []).append(persona)
    lineas = [f"@{TIPOS.get(tipo, 'misc')}{{{clave},"]
    for campo, personas in creadores.items():
        lineas.append(f"  {campo} = {{{' and '.join(personas)}}},")
    fecha = (datos.get("date") or "").split(" ")[0]
    anio = fecha[:4] if re.match(r"^\d{4}", fecha) else fecha
    if anio:
        lineas.append(f"  date = {{{anio}}},")
    for z, b in CAMPOS.items():
        valor = (datos.get(z) or "").strip()
        if not valor or (z == "edition" and valor in ("1", "1.ª", "1a", "primera")):
            continue
        lineas.append(f"  {b} = {{{_escapar(valor) if z not in ('url', 'DOI') else valor}}},")
    if tipo == "thesis" and datos.get("thesisType"):
        lineas.append(f"  type = {{{datos['thesisType']}}},")
    lineas.append("}")
    return "\n".join(lineas)


def main() -> int:
    ap = argparse.ArgumentParser(description="referencias.bib de un documento desde Zotero (APA 7)")
    ap.add_argument("tex", type=Path)
    ap.add_argument("--aplicar", action="store_true", help="escribe <carpeta>/referencias.bib (por omisión simula)")
    args = ap.parse_args()
    if not args.tex.is_file():
        print(f"No existe: {args.tex}", file=sys.stderr)
        return 2
    db = ruta_zotero()
    if db is None or not db.is_file():
        print("No encuentro zotero.sqlite (ZOTERO_DB de core/env.sh).", file=sys.stderr)
        return 2
    claves = claves_citadas(args.tex)
    con = sqlite3.connect(f"file:{db}?immutable=1", uri=True)
    bloques, faltan = [], []
    for k in claves:
        e = entrada(con, k)
        (bloques.append(e) if e else faltan.append(k))
    con.close()
    contenido = (f"% referencias.bib — GENERADO por docencia/scripts/bib-zotero.py desde Zotero para "
                 f"{args.tex.name}; no editar (se corrige en Zotero y se regenera)\n\n" + "\n\n".join(bloques) + "\n")
    destino = args.tex.resolve().parent / "referencias.bib"
    if args.aplicar:
        destino.write_text(contenido, encoding="utf-8")
        print(f"escrito {destino} ({len(bloques)} entradas)")
    else:
        print(contenido)
        print(f"SIMULACIÓN: {len(bloques)} entradas para {destino} (usa --aplicar)")
    for k in faltan:
        print(f"FALTA en Zotero: {k}", file=sys.stderr)
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
