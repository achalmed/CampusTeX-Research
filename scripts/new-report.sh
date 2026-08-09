#!/usr/bin/env bash
# ============================================================
# new-report.sh — Crea un documento de gestión docente (academic-report)
# ============================================================
# Uso:
#   ./scripts/new-report.sh COURSE_DIR TIPO "TÍTULO"
#
# TIPO: silabo, calendario, nota-docente, rubrica, manual, guia
#   (los que existan en templates/report/).
#
# Copia la plantilla a la carpeta 00–09 que le corresponde y rellena metadatos.
# Compila con build.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$1"; TIPO="$2"; TITULO="$3"
is_course "$COURSE" || die "No parece un curso: $COURSE"

# TIPO → subcarpeta 00–09 destino
case "$TIPO" in
  silabo)       SUB=00_ADMINISTRACION ;;
  calendario)   SUB=00_ADMINISTRACION ;;
  nota-docente) SUB=01_PLANIFICACION ;;
  rubrica)      SUB=04_EVALUACIONES/rubricas ;;
  manual|guia)  SUB=06_RECURSOS ;;
  *) die "TIPO no reconocido: $TIPO" ;;
esac
TPL="$FW_DIR/templates/report/$TIPO/$TIPO.tex"
[[ -f "$TPL" ]] || die "No existe la plantilla templates/report/$TIPO/"
DESTDIR="$COURSE/$SUB"; mkdir -p "$DESTDIR"
DEST="$DESTDIR/$TIPO.tex"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

CURSO_LABEL="$(basename "$COURSE" | sed -E 's/^course_[0-9]+_//; s/[_-]+/ /g')"
DOC="$(config_get docente)"; DT="$(config_get docente_titulo)"; [[ -n "$DT" ]] && DOC="$DOC $DT"
cp "$TPL" "$DEST"
sed -i -E \
  -e "s|\\\\curso\{[^}]*\}|\\\\curso{${CURSO_LABEL}}|" \
  -e "s|\\\\docente\{[^}]*\}|\\\\docente{${DOC}}|" \
  -e "s|\\\\universidad\{[^}]*\}|\\\\universidad{$(config_get universidad)}|" \
  -e "s|\\\\periodo\{[^}]*\}|\\\\periodo{Semestre $(config_get ciclo)}|" \
  -e "s|\\\\titulodocumento\{[^}]*\}|\\\\titulodocumento{${TITULO}}|" \
  "$DEST"

ok "Documento creado: ${DEST}"
echo "Compila:  ./scripts/build.sh \"$DEST\""
