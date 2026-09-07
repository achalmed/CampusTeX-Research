#!/usr/bin/env bash
# publish-web.sh — publica un dictado en 04 index/cursos por HARDLINK (F5.2).
#   ./scripts/publish-web.sh <COURSE_DIR> <AAAA-ciclo> [--aplicar]
# Lee <COURSE_DIR>/09_SEMESTRES/<periodo>/dictado.yml; simula sin --aplicar.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/publicar-web.py" "$@"
