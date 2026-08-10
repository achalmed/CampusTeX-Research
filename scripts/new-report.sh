#!/usr/bin/env bash
# ============================================================
# new-report.sh — Crea un documento de gestión docente (academic-report)
# ============================================================
# Uso:
#   ./scripts/new-report.sh COURSE_DIR TIPO "TÍTULO"
#
# TIPO: uno de los subdirectorios reales de templates/report/
#   (hoy: silabo, calendario, nota-docente, rubrica). Se validan en tiempo
#   de ejecución contra las plantillas existentes.
#
# Copia la plantilla a la carpeta 00–09 que le corresponde y rellena metadatos.
# Compila con build.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$1"; TIPO="$2"; TITULO="$3"
is_course "$COURSE" || die "No parece un curso: $COURSE"

# Tipos válidos = subdirectorios REALES de templates/report/ que traen su .tex.
# Se listan dinámicamente para que el script no prometa plantillas inexistentes.
REPORT_TPL_DIR="$FW_DIR/templates/report"
VALIDOS=""
for _d in "$REPORT_TPL_DIR"/*/; do
  _t="$(basename "$_d")"
  [[ -f "$_d/$_t.tex" ]] && VALIDOS="${VALIDOS:+$VALIDOS }$_t"
done
[[ -n "$VALIDOS" ]] || die "No hay plantillas en $REPORT_TPL_DIR/"

# Rechazo temprano con mensaje claro si el TIPO no corresponde a una plantilla real.
case " $VALIDOS " in
  *" $TIPO "*) : ;;
  *) die "TIPO no reconocido: '$TIPO'. Válidos: $VALIDOS" ;;
esac

# TIPO → subcarpeta 00–09 destino (solo tipos ya validados contra las plantillas)
case "$TIPO" in
  silabo)       SUB=00_ADMINISTRACION ;;
  calendario)   SUB=00_ADMINISTRACION ;;
  nota-docente) SUB=01_PLANIFICACION ;;
  rubrica)      SUB=04_EVALUACIONES/rubricas ;;
  *)            SUB=06_RECURSOS ;;
esac
TPL="$REPORT_TPL_DIR/$TIPO/$TIPO.tex"
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
