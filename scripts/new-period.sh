#!/usr/bin/env bash
# ============================================================
# new-period.sh — Crea un dictado (periodo) en 09_SEMESTRES/
# ============================================================
# Uso:
#   ./scripts/new-period.sh COURSE_DIR PERIODO
#
# Ejemplo:
#   ./scripts/new-period.sh "$C" 2026-II
#
# Copia scaffolds/period al curso como 09_SEMESTRES/<periodo>/:
# registro privado (estudiantes, calificaciones, cronograma,
# evaluaciones_aplicadas, evidencias) + publicacion (MOOC por sesión).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 2 ]] || usage

COURSE="$1"
PERIODO="$2"

is_course "$COURSE" || die "No parece un curso: $COURSE"
[[ -d "$SCAFFOLDS_DIR/period" ]] || die "Falta $SCAFFOLDS_DIR/period"

DEST="$COURSE/09_SEMESTRES/$PERIODO"
[[ -e "$DEST" ]] && die "Ya existe el periodo: $DEST"

mkdir -p "$COURSE/09_SEMESTRES"
cp -a "$SCAFFOLDS_DIR/period" "$DEST"
ok "Periodo creado: $DEST"
