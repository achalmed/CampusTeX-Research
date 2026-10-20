#!/usr/bin/env python3
"""areas.py — el vocabulario cerrado de áreas (config/areas.yml) y su reparto de cursos entre los pubs.

Uso:
  python3 scripts/areas.py listar                 # tabla área → pub → cursos (principal y secundarios)
  python3 scripts/areas.py verificar [CURSO.yml…]  # cada `area` en el vocabulario; sin argumentos, todos los cursos
  python3 scripts/areas.py pub CURSO              # el pub que aloja un curso (carpeta de web/_pubs; vacío si no hay)
Salida: 0 bien · 1 algún curso fuera del vocabulario o sin área · 2 error de uso.
El primer valor de `area` es el área principal y decide el pub (web/docs/plataforma-educativa.md §5).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

FRAMEWORK = Path(__file__).resolve().parents[1]
VOCABULARIO = FRAMEWORK / "config" / "areas.yml"
CURSOS = FRAMEWORK / "contenido" / "cursos"


def vocabulario() -> dict[str, dict]:
    """{id: {id, nombre, pub}} en el orden del archivo."""
    return {a["id"]: a for a in yaml.safe_load(VOCABULARIO.read_text(encoding="utf-8"))["areas"]}


def areas_de(curso_yml: Path) -> list[str]:
    return list((yaml.safe_load(curso_yml.read_text(encoding="utf-8")) or {}).get("area") or [])


def pub_de(curso_yml: Path, voc: dict[str, dict] | None = None) -> str | None:
    """El pub del área principal del curso, o None si no tiene área válida o el área aún no tiene sitio."""
    voc = voc or vocabulario()
    a = areas_de(curso_yml)
    return voc[a[0]]["pub"] if a and a[0] in voc else None


def problemas(curso_yml: Path, voc: dict[str, dict]) -> list[str]:
    a = areas_de(curso_yml)
    if not a:
        return ["sin `area`"]
    return [f"área «{x}» fuera de config/areas.yml" for x in a if x not in voc]


def todos() -> list[Path]:
    return sorted(CURSOS.glob("*/curso.yml"))


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in {"listar", "verificar", "pub"}:
        print(__doc__, file=sys.stderr)
        return 2
    voc = vocabulario()
    orden, args = argv[0], argv[1:]
    if orden == "verificar":
        rutas = [Path(x) for x in args] or todos()
        malos = 0
        for r in rutas:
            for p in problemas(r, voc):
                print(f"[XX] {r.parent.name}: {p}")
                malos += 1
        if not args:
            print(f"{len(rutas)} cursos revisados · {malos} problema(s)")
        return 1 if malos else 0
    if orden == "pub":
        if len(args) != 1:
            print(__doc__, file=sys.stderr)
            return 2
        print(pub_de(CURSOS / args[0] / "curso.yml", voc) or "")
        return 0
    principal: dict[str, list[str]] = {k: [] for k in voc}
    secundario: dict[str, list[str]] = {k: [] for k in voc}
    for r in todos():
        a = [x for x in areas_de(r) if x in voc]
        if a:
            principal[a[0]].append(r.parent.name)
            for x in a[1:]:
                secundario[x].append(r.parent.name)
    for k, v in voc.items():
        print(f"{v['nombre']}  →  {v['pub'] or '(sin sitio)'}")
        print(f"    vive aquí ({len(principal[k])}): {', '.join(principal[k]) or '—'}")
        if secundario[k]:
            print(f"    se lista también ({len(secundario[k])}): {', '.join(secundario[k])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
