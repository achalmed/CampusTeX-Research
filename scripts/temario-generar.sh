#!/usr/bin/env bash
# temario-generar.sh — fachada Bash del generador de vistas del currículo (F5.1).
# El currículo de cada curso vive en docencia/cursos/<slug>/curso.yml; de ahí se generan README,
# ficha web, temario del learning-skill y checklist de estudio.
#   ./scripts/temario-generar.sh migrar   [--aplicar] [CURSO_DIR...]
#   ./scripts/temario-generar.sh generar  [--aplicar] [--que readme,esqueleto,web,skill,resumen] [CURSO_DIR...]
#   ./scripts/temario-generar.sh verificar [CURSO_DIR...]
# Sin --aplicar es simulación. Requiere python3 + pyyaml.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo "Falta python3" >&2; exit 5; }
exec python3 "$SCRIPT_DIR/temario.py" "$@"
