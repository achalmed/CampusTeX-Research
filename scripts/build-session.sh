#!/usr/bin/env bash
# ============================================================
# build-session.sh — Compila las diapositivas de una sesión
# ============================================================
# Uso:
#   ./scripts/build-session.sh NUM
#
# Ejemplo:
#   ./scripts/build-session.sh 02
#
# Detecta el formato automáticamente:
#   - slides/*.qmd  → quarto render (HTML RevealJS y/o PDF
#                     según el YAML del propio .qmd)
#   - slides/**.tex → LaTeX con motor autodetectado
#                     (compila TODOS los .tex de la sesión,
#                     útil en sesiones con varios decks como
#                     session_05_apa)
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,17p' "${BASH_SOURCE[0]}"; exit 1; }

DIR="$(session_dir "$1")" || die "No existe la sesión $1 en course/sessions/"
SLIDES="$DIR/slides"
info "Sesión: ${DIR#"$ROOT_DIR"/}"

# --- Proyecto Quarto (excepción: sesión 4) -------------------
qmd="$(find "$SLIDES" -maxdepth 1 -name '*.qmd' | head -1)"
if [[ -n "$qmd" ]]; then
  require_cmd quarto
  info "Proyecto Quarto detectado: $(basename "$qmd")"
  ( cd "$SLIDES" && quarto render "$(basename "$qmd")" )
  ok "Render Quarto completado."
  exit 0
fi

# --- Documentos LaTeX ----------------------------------------
# Se compilan todos los .tex (hasta 2 niveles: master + subdecks),
# excluyendo directorios generados.
mapfile -t texfiles < <(find "$SLIDES" -maxdepth 2 -name '*.tex' \
  -not -path '*index_files*' | sort)
[[ ${#texfiles[@]} -gt 0 ]] || die "No hay .tex ni .qmd en $SLIDES"

fail=0
for tex in "${texfiles[@]}"; do
  if compile_tex "$tex"; then
    ok "PDF generado: ${tex%.tex}.pdf"
  else
    error "Falló la compilación de: $tex"
    fail=1
  fi
done
exit "$fail"
