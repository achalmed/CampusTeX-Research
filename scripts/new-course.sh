#!/usr/bin/env bash
# ============================================================
# new-course.sh — Crea un curso nuevo (estructura 00–09)
# ============================================================
# Uso:
#   ./scripts/new-course.sh ACADEMIC_CLASS_DIR NUM "TÍTULO"
#
# Ejemplo:
#   ./scripts/new-course.sh ~/Documents/Academic_Class-Estadistica 00 "Estadística Descriptiva"
#
# Copia scaffolds/course (00–09) al Academic_Class
# indicado como course_NN_<slug>/.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage

AC="$1"
NUM="$(printf '%02d' "$((10#$2))")"
TITLE="$3"
SLUG="$(slugify "$TITLE")"

[[ -d "$AC" ]] || die "No existe el Academic_Class: $AC"
[[ -d "$SCAFFOLDS_DIR/course" ]] || die "Falta $SCAFFOLDS_DIR/course"

DEST="$AC/course_${NUM}_${SLUG}"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

info "Creando curso $NUM: '$TITLE'"
cp -a "$SCAFFOLDS_DIR/course" "$DEST"

cat > "$DEST/README.md" <<EOF
# $TITLE

Curso \`course_${NUM}_${SLUG}\`. Estructura estándar 00–09
(ver \`~/Documents/Academic_Class_Framework/README.md\`).

- \`00_ADMINISTRACION\` … \`08_INVESTIGACION\` — contenido canónico y atemporal del curso.
- \`09_SEMESTRES/<periodo>\` — cada dictado: registro privado + publicación MOOC
  (crear con \`new-period.sh\`; se congela por sesión).
EOF

ok "Curso creado: $DEST"
echo "Siguiente: ./scripts/new-session.sh \"$DEST\" 01 \"Título de la sesión\""
