#!/usr/bin/env bash
# ============================================================
# build-session.sh — Compila el/los deck(s) de una sesión
# ============================================================
# Uso:
#   ./scripts/build-session.sh COURSE_DIR NUM
#
# Ejemplo:
#   ./scripts/build-session.sh "$C" 02
#
# Compila lo que haya en 02_Clase/:
#   - *.qmd → quarto render
#   - *.tex → LaTeX con motor autodetectado (todos los .tex,
#             útil cuando 02_Clase/ tiene varios decks)
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 2 ]] || { sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$1"
DIR="$(session_dir "$COURSE" "$2")" || die "No existe la sesión $2 en $COURSE/03_SESIONES/"
CLASE="$DIR/02_Clase"
[[ -d "$CLASE" ]] || die "Falta 02_Clase/ en $(basename "$DIR")"
info "Sesión: $(basename "$DIR")"

# --- Quarto ---------------------------------------------------
qmd="$(find "$CLASE" -maxdepth 1 -name '*.qmd' | head -1)"
if [[ -n "$qmd" ]]; then
  require_cmd quarto
  info "Proyecto Quarto: $(basename "$qmd")"
  ( cd "$CLASE" && quarto render "$(basename "$qmd")" )
  ok "Render Quarto completado."; exit 0
fi

# --- LaTeX (todos los .tex, hasta 2 niveles) -----------------
mapfile -t texfiles < <(find "$CLASE" -maxdepth 2 -name '*.tex' -not -path '*index_files*' | sort)
[[ ${#texfiles[@]} -gt 0 ]] || die "No hay .tex ni .qmd en $CLASE"

fail=0
for tex in "${texfiles[@]}"; do
  if compile_tex "$tex"; then ok "PDF: ${tex%.tex}.pdf"
  else error "Falló: $tex"; fail=1; fi
done
exit "$fail"
