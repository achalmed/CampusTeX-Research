#!/usr/bin/env bash
# ============================================================
# build-session.sh — Compila el artefacto de una sesión (M5)
# ============================================================
# Uso:
#   ./scripts/build-session.sh CURSO NN        # CURSO: ruta o slug
#
# Compila el artefacto declarado en sesion.yml (*.qmd → quarto render; *.tex → LuaLaTeX).
# Si no hay artefacto declarado, compila todos los .tex/.qmd de la raíz de la sesión.
# Un artefacto que no sea deck (cuaderno, script, libro) no se compila: se informa.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 2 ]] || { sed -n '2,11p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$(course_dir "$1")" || die "No es un curso: $1"
DIR="$(session_dir "$COURSE" "$2")" || die "No existe la sesión $2 en $COURSE/03-sesiones/"
info "Sesión: $(basename "$DIR")"

ART="$(session_artifact "$DIR")"
declare -a objetivos=()
if [[ -n "$ART" ]]; then
  [[ -f "$DIR/$ART" ]] || die "El artefacto declarado no existe: $ART"
  case "${ART##*.}" in
    tex|qmd) objetivos=("$DIR/$ART") ;;
    *) ok "Artefacto '$ART' ($(yaml_get "$DIR/sesion.yml" tipo)): no se compila."; exit 0 ;;
  esac
else
  mapfile -t objetivos < <(find "$DIR" -maxdepth 1 \( -name '*.tex' -o -name '*.qmd' \) -not -path '*index_files*' | sort)
  [[ ${#objetivos[@]} -gt 0 ]] || die "Sin artefacto declarado ni .tex/.qmd en $DIR"
fi

fail=0
for f in "${objetivos[@]}"; do
  case "$f" in
    *.qmd) require_cmd quarto; info "Quarto: $(basename "$f")"; ( cd "$DIR" && quarto render "$(basename "$f")" ) && ok "Render: $f" || { error "Falló: $f"; fail=1; } ;;
    *.tex) compile_tex "$f" && ok "PDF: ${f%.tex}.pdf" || { error "Falló: $f"; fail=1; } ;;
  esac
done
exit "$fail"
