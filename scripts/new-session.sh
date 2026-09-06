#!/usr/bin/env bash
# ============================================================
# new-session.sh — Crea una sesión nueva en un curso
# ============================================================
# Uso:
#   ./scripts/new-session.sh COURSE_DIR NUM "TÍTULO" [--quarto]
#
# Ejemplos:
#   ./scripts/new-session.sh ~/Documents/Academic_Class_Framework/areas/Academic_Class-Estadistica/course_00_descriptiva 07 "Marco Teórico"
#   ./scripts/new-session.sh "$C" 08 "Análisis de Datos" --quarto
#
# Copia scaffolds/session (anatomía 01_Antes…07_Notas)
# al curso como 03_SESIONES/SNN_slug/ y rellena las plantillas
# con los datos de config/course.yml. Por defecto el deck es
# LaTeX Beamer (02_Clase/slides.tex); con --quarto, Quarto RevealJS.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,18p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage

COURSE="$1"
NUM="$(printf '%02d' "$((10#$2))")"
TITLE="$3"
FORMAT="latex"
[[ "${4:-}" == "--quarto" ]] && FORMAT="quarto"

is_course "$COURSE" || die "No parece un curso (falta 00_ADMINISTRACION/03_SESIONES): $COURSE"
[[ -d "$SCAFFOLDS_DIR/session" ]] || die "Falta $SCAFFOLDS_DIR/session"

SLUG="$(slugify "$TITLE")"
if session_dir "$COURSE" "$NUM" >/dev/null 2>&1; then
  die "Ya existe una sesión con número $NUM: $(session_dir "$COURSE" "$NUM")"
fi
DEST="$COURSE/03_SESIONES/S${NUM}_${SLUG}"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

# Etiqueta del curso desde el nombre de carpeta (course_NN_a_b -> "a b")
COURSE_LABEL="$(basename "$COURSE" | sed -E 's/^course_[0-9]+_//; s/[_-]+/ /g')"

info "Creando sesión $NUM: '$TITLE' (formato: $FORMAT)"
cp -a "$SCAFFOLDS_DIR/session" "$DEST"

# Elegir formato del deck
if [[ "$FORMAT" == "quarto" ]]; then rm -f "$DEST/02_Clase/slides.tex"
else rm -f "$DEST/02_Clase/slides.qmd"; fi

# Rellenar {{PLACEHOLDERS}} en todos los archivos de texto
while IFS= read -r -d '' f; do
  sed -i \
    -e "s|{{NUMBER}}|$NUM|g" \
    -e "s|{{TITLE}}|$TITLE|g" \
    -e "s|{{SLUG}}|$SLUG|g" \
    -e "s|{{DATE}}|$(date +%Y-%m-%d)|g" \
    -e "s|{{COURSE}}|$COURSE_LABEL|g" \
    -e "s|{{COURSE_SHORT}}|$COURSE_LABEL|g" \
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
    "$f"
done < <(find "$DEST" -type f \( -name '*.md' -o -name '*.yml' -o -name '*.tex' -o -name '*.qmd' \) -print0)

# Logo institucional junto al deck (autocontenido)
LOGO="$FW_DIR/$(config_get logo)"
[[ -f "$LOGO" ]] && cp "$LOGO" "$DEST/02_Clase/cau-logo.png"

ok "Sesión creada: $DEST"
echo "Siguiente: edita 02_Clase/ y compila con ./scripts/build-session.sh \"$COURSE\" $NUM"
