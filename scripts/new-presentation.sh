#!/usr/bin/env bash
# ============================================================
# new-presentation.sh — Crea las diapositivas de una sesión (academic-beamer)
# ============================================================
# Uso:
#   ./scripts/new-presentation.sh CURSO NN "TÍTULO" [--tipo TIPO]
#
# CURSO: ruta o slug. NN: número de sesión (sNN-* del curso).
# TIPO (por defecto clase): clase, conferencia, seminario, ponencia, workshop,
#   defensa-tesis, institucional, masterclass (los que existan en templates/presentation/).
#
# Copia la plantilla al artefacto de la sesión (sesion.yml: artefacto, o deck.tex si no está
# declarado, en cuyo caso lo declara) y rellena título/autor/fecha desde config. Compila con build.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$(course_dir "$1")" || die "No es un curso: $1"
NN="$2"; TITULO="$3"; TIPO="clase"
[[ "${4:-}" == "--tipo" ]] && TIPO="$5"

SES="$(session_dir "$COURSE" "$NN")" || die "No existe la sesión $NN en $COURSE/03-sesiones/"
TPL="$FW_DIR/templates/presentation/$TIPO/$TIPO.tex"
[[ -f "$TPL" ]] || die "No existe la plantilla templates/presentation/$TIPO/"
ART="$(session_artifact "$SES")"
[[ "$ART" == *.tex ]] || ART="deck.tex"
DEST="$SES/$ART"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

DOC="$(config_get docente)"; DT="$(config_get docente_titulo)"; [[ -n "$DT" ]] && DOC="$DOC $DT"
cp "$TPL" "$DEST"
sed -i -E \
  -e "s|\\\\title\{[^}]*\}|\\\\title{${TITULO}}|" \
  -e "s|\\\\author\{[^}]*\}|\\\\author{${DOC}}|" \
  -e "s|\\\\institute\{[^}]*\}|\\\\institute{$(config_get universidad)}|" \
  -e "s|\\\\date\{[^}]*\}|\\\\date{Semestre $(config_get ciclo)}|" \
  "$DEST"
set_identidad "$DEST" "deck de la sesión ${NN}: ${TITULO}"
if [[ "$(session_artifact "$SES")" != "$ART" ]]; then
  if grep -qE '^artefacto:' "$SES/sesion.yml"; then sed -i -E "s|^artefacto:.*|artefacto: $ART|" "$SES/sesion.yml"
  else sed -i -E "s|^(estado:.*)$|\1\nartefacto: $ART|" "$SES/sesion.yml"; fi
  info "sesion.yml: artefacto: $ART"
fi
ok "Diapositivas creadas: ${DEST}"
echo "Compila:  ./scripts/build.sh \"$DEST\""
