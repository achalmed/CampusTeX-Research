#!/usr/bin/env bash
# ============================================================
# new-presentation.sh — Crea las diapositivas de una sesión (academic-beamer)
# ============================================================
# Uso:
#   ./scripts/new-presentation.sh COURSE_DIR NN "TÍTULO" [--tipo TIPO]
#
# NN: número de sesión (usa la sesión SNN_* del curso).
# TIPO (por defecto clase): clase, conferencia, seminario, ponencia, workshop,
#   defensa-tesis, institucional, masterclass (los que existan en templates/presentation/).
#
# Copia la plantilla a  <sesión>/02_Clase/diapositivas.tex  y rellena
# título/autor/fecha desde config. Compila con build.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$1"; NN="$2"; TITULO="$3"; TIPO="clase"
[[ "${4:-}" == "--tipo" ]] && TIPO="$5"
is_course "$COURSE" || die "No parece un curso: $COURSE"

SES="$(session_dir "$COURSE" "$NN")" || die "No existe la sesión $NN en $COURSE/03_SESIONES/"
TPL="$FW_DIR/templates/presentation/$TIPO/$TIPO.tex"
[[ -f "$TPL" ]] || die "No existe la plantilla templates/presentation/$TIPO/"
DEST="$SES/02_Clase/diapositivas.tex"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"
mkdir -p "$SES/02_Clase"

DOC="$(config_get docente)"; DT="$(config_get docente_titulo)"; [[ -n "$DT" ]] && DOC="$DOC $DT"
cp "$TPL" "$DEST"
sed -i -E \
  -e "s|\\\\title\{[^}]*\}|\\\\title{${TITULO}}|" \
  -e "s|\\\\author\{[^}]*\}|\\\\author{${DOC}}|" \
  -e "s|\\\\institute\{[^}]*\}|\\\\institute{$(config_get universidad)}|" \
  -e "s|\\\\date\{[^}]*\}|\\\\date{Semestre $(config_get ciclo)}|" \
  "$DEST"

set_identidad "$DEST" "deck de la sesión ${NN}: ${TITULO}"
ok "Diapositivas creadas: ${DEST}"
echo "Compila:  ./scripts/build.sh \"$DEST\""
