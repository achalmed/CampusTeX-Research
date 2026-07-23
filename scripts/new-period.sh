#!/usr/bin/env bash
# ============================================================
# new-period.sh — Crea un dictado (periodo) en 11_SEMESTRES/
# ============================================================
# Uso:
#   ./scripts/new-period.sh COURSE_DIR PERIODO
#
# Ejemplo:
#   ./scripts/new-period.sh "$C" 2026-II
#
# Copia _PLANTILLAS/Plantilla_Periodo al curso como
# 11_SEMESTRES/<periodo>/ (estudiantes, calificaciones,
# evidencias, publicacion…).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 2 ]] || usage

COURSE="$1"
PERIODO="$2"

is_course "$COURSE" || die "No parece un curso: $COURSE"
[[ -d "$PLANTILLAS_DIR/Plantilla_Periodo" ]] || die "Falta $PLANTILLAS_DIR/Plantilla_Periodo"

DEST="$COURSE/11_SEMESTRES/$PERIODO"
[[ -e "$DEST" ]] && die "Ya existe el periodo: $DEST"

mkdir -p "$COURSE/11_SEMESTRES"
cp -a "$PLANTILLAS_DIR/Plantilla_Periodo" "$DEST"
ok "Periodo creado: $DEST"
