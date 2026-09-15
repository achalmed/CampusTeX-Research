#!/usr/bin/env bash
# ============================================================
# new-report.sh — Crea un documento de gestión docente (academic-report)
# ============================================================
# Uso:
#   ./scripts/new-report.sh CURSO TIPO "TÍTULO"
#
# CURSO: ruta o slug. TIPO: uno de los subdirectorios reales de templates/report/
#   (hoy: silabo, calendario, nota-docente, rubrica).
#
# Destino: 01-diseno/ (sílabo, calendario, nota docente), 01-diseno/rubricas/ (rúbrica),
# 05-recursos/ (otros). Rellena metadatos desde curso.yml y config. Compila con build.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$(course_dir "$1")" || die "No es un curso: $1"
TIPO="$2"; TITULO="$3"

REPORT_TPL_DIR="$FW_DIR/templates/report"
VALIDOS=""
for _d in "$REPORT_TPL_DIR"/*/; do
  _t="$(basename "$_d")"
  [[ -f "$_d/$_t.tex" ]] && VALIDOS="${VALIDOS:+$VALIDOS }$_t"
done
[[ -n "$VALIDOS" ]] || die "No hay plantillas en $REPORT_TPL_DIR/"
case " $VALIDOS " in
  *" $TIPO "*) : ;;
  *) die "TIPO no reconocido: '$TIPO'. Válidos: $VALIDOS" ;;
esac
case "$TIPO" in
  silabo|calendario|nota-docente) SUB=01-diseno ;;
  rubrica)                        SUB=01-diseno/rubricas ;;
  *)                              SUB=05-recursos ;;
esac
TPL="$REPORT_TPL_DIR/$TIPO/$TIPO.tex"
DESTDIR="$COURSE/$SUB"; mkdir -p "$DESTDIR"
DEST="$DESTDIR/$TIPO.tex"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

CURSO_LABEL="$(course_title "$COURSE")"
DOC="$(config_get docente)"; DT="$(config_get docente_titulo)"; [[ -n "$DT" ]] && DOC="$DOC $DT"
cp "$TPL" "$DEST"
sed -i -E \
  -e "s|\\\\curso\{[^}]*\}|\\\\curso{${CURSO_LABEL}}|" \
  -e "s|\\\\docente\{[^}]*\}|\\\\docente{${DOC}}|" \
  -e "s|\\\\universidad\{[^}]*\}|\\\\universidad{$(config_get universidad)}|" \
  -e "s|\\\\periodo\{[^}]*\}|\\\\periodo{Semestre $(config_get ciclo)}|" \
  -e "s|\\\\titulodocumento\{[^}]*\}|\\\\titulodocumento{${TITULO}}|" \
  "$DEST"
set_identidad "$DEST" "${TIPO//-/ }: ${TITULO}"
ok "Documento creado: ${DEST}"
echo "Compila:  ./scripts/build.sh \"$DEST\""
