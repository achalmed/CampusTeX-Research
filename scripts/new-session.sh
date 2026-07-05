#!/usr/bin/env bash
# ============================================================
# new-session.sh — Crea una nueva sesión (unidad didáctica)
# ============================================================
# Uso:
#   ./scripts/new-session.sh NUM "TÍTULO" [--quarto]
#
# Ejemplos:
#   ./scripts/new-session.sh 07 "Marco Teórico"
#   ./scripts/new-session.sh 08 "Análisis de Datos" --quarto
#
# Genera course/sessions/session_NN_slug/ con la estructura
# canónica completa, rellenando las plantillas de
# templates/session/ con los datos de config/course.yml.
# Por defecto las diapositivas son LaTeX Beamer; con --quarto
# se genera un proyecto Quarto RevealJS.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,17p' "${BASH_SOURCE[0]}"; exit 1; }

[[ $# -ge 2 ]] || usage
NUM="$(printf '%02d' "$((10#$1))")"
TITLE="$2"
FORMAT="latex"
[[ "${3:-}" == "--quarto" ]] && FORMAT="quarto"

SLUG="$(slugify "$TITLE")"
DEST="$SESSIONS_DIR/session_${NUM}_${SLUG}"

if session_dir "$NUM" >/dev/null 2>&1; then
  die "Ya existe una sesión con el número $NUM: $(session_dir "$NUM")"
fi
[[ -d "$DEST" ]] && die "Ya existe: $DEST"

info "Creando sesión $NUM: '$TITLE' (formato: $FORMAT)"
mkdir -p "$DEST"/{slides,teaching,practice,evaluation,homework,resources/readings,archive}
touch "$DEST"/{practice,evaluation,homework,resources/readings,archive}/.gitkeep

# render_template ORIGEN DESTINO — sustituye {{PLACEHOLDERS}}
render_template() {
  sed -e "s|{{NUMBER}}|$NUM|g" \
      -e "s|{{TITLE}}|$TITLE|g" \
      -e "s|{{SLUG}}|$SLUG|g" \
      -e "s|{{DATE}}|$(date +%Y-%m-%d)|g" \
      -e "s|{{COURSE}}|$(config_get curso)|g" \
      -e "s|{{COURSE_SHORT}}|$(config_get curso_corto)|g" \
      -e "s|{{CYCLE}}|$(config_get ciclo)|g" \
      -e "s|{{TEACHER}}|$(config_get docente)|g" \
      -e "s|{{EMAIL}}|$(config_get email)|g" \
      -e "s|{{INSTITUTION}}|$(config_get institucion)|g" \
      -e "s|{{UNIVERSITY}}|$(config_get universidad)|g" \
      -e "s|{{THEME}}|$(config_get tema_beamer Madrid)|g" \
      -e "s|{{ASPECT}}|$(config_get aspecto 169)|g" \
      -e "s|{{DURATION}}|$(config_get duracion_sesion_min 180)|g" \
      -e "s|{{MODALITY}}|$(config_get modalidad presencial)|g" \
      -e "s|{{LEVEL}}|$(config_get nivel pregrado)|g" \
      -e "s|{{FORMAT}}|$FORMAT|g" \
      "$1" > "$2"
}

T="$TEMPLATES_DIR/session"
render_template "$T/metadata.yml"        "$DEST/metadata.yml"
render_template "$T/README.md"           "$DEST/README.md"
render_template "$T/lesson_plan.md"      "$DEST/teaching/lesson_plan.md"
render_template "$T/teacher_notes.md"    "$DEST/teaching/teacher_notes.md"
render_template "$T/retrospective.md"    "$DEST/teaching/retrospective.md"
render_template "$T/links.md"            "$DEST/resources/links.md"

if [[ "$FORMAT" == "quarto" ]]; then
  render_template "$T/slides.qmd" "$DEST/slides/slides.qmd"
else
  render_template "$T/slides.tex" "$DEST/slides/slides.tex"
fi

# Logo institucional junto a las diapositivas (los .tex lo
# referencian en su propio directorio para ser autocontenidos).
LOGO="$ROOT_DIR/$(config_get logo)"
[[ -f "$LOGO" ]] && cp "$LOGO" "$DEST/slides/cau-logo.png"

ok "Sesión creada: ${DEST#"$ROOT_DIR"/}"
echo
echo "Siguientes pasos:"
echo "  1. Completa $DEST/metadata.yml"
echo "  2. Edita las diapositivas en $DEST/slides/"
echo "  3. Compila con: ./scripts/build-session.sh $NUM"
