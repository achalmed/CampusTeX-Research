#!/usr/bin/env bash
# publish-web.sh — publica un dictado en 04 index/cursos por HARDLINK (F5.2 / M5).
#   ./scripts/publish-web.sh DICTADO [--aplicar]     # DICTADO: clave o ruta de docencia/dictados/<clave>
# Lee dictado.yml (web.materia, web.edicion, sesiones[]); simula sin --aplicar.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/publicar-web.py" "$@"
