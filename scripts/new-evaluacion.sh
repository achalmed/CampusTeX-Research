#!/usr/bin/env bash
# ============================================================
# new-evaluacion.sh — Crea una evaluación en un curso
# ============================================================
# Uso:
#   ./scripts/new-evaluacion.sh COURSE_DIR TIPO "TÍTULO" [--fecha AAAAMMDD]
#
# Ejemplo:
#   ./scripts/new-evaluacion.sh "$C" examen-desarrollo "Examen Parcial 01"
#   ./scripts/new-evaluacion.sh "$C" 04 "Práctica Calificada 02" --fecha 20260815
#
# TIPO (número 01–12 o nombre): examen-desarrollo, examen-objetivo,
#   examen-problemas, practica-calificada, practica-dirigida, laboratorio,
#   control-de-lectura, examen-oral, caso-estudio, tarea, banco-de-preguntas,
#   solucionario.
#
# Copia la plantilla a  <curso>/04_EVALUACIONES/<subcarpeta>/AAAAMMDD_SIGLA.tex,
# rellena los metadatos (curso, docente, universidad, periodo, tipo, fecha) desde
# config/course.yml y el nombre del curso. Compila con build-evaluacion.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage

COURSE="$1"; TIPO="$2"; TITULO="$3"; FECHA=""
[[ "${4:-}" == "--fecha" ]] && FECHA="$5"
[[ -n "$FECHA" ]] || FECHA="$(date +%Y%m%d)"

is_course "$COURSE" || die "No parece un curso (falta 00_ADMINISTRACION/03_SESIONES): $COURSE"

# --- Tabla: TIPO → (NN plantilla · subcarpeta de 04_EVALUACIONES · SIGLA) -----
case "$TIPO" in
  01|examen-desarrollo)     NN=01; SUB=examen_parcial;  SIG=EP  ;;
  02|examen-objetivo)       NN=02; SUB=examen_parcial;  SIG=EP  ;;
  03|examen-problemas)      NN=03; SUB=examen_parcial;  SIG=EP  ;;
  04|practica-calificada)   NN=04; SUB=practicas;       SIG=PC  ;;
  05|practica-dirigida)     NN=05; SUB=practicas;       SIG=PD  ;;
  06|laboratorio)           NN=06; SUB=laboratorios;    SIG=LAB ;;
  07|control-de-lectura)    NN=07; SUB=tareas;          SIG=CL  ;;
  08|examen-oral)           NN=08; SUB=examen_final;    SIG=EO  ;;
  09|caso-estudio)          NN=09; SUB=proyectos;       SIG=CASO;;
  10|tarea)                 NN=10; SUB=tareas;          SIG=TAR ;;
  11|banco-de-preguntas)    NN=11; SUB=banco_preguntas; SIG=BP  ;;
  12|solucionario)          NN=12; SUB=soluciones;      SIG=SOL ;;
  *) die "TIPO no reconocido: $TIPO (01–12 o nombre; ver --help)" ;;
esac

TPL="$(find "$EVAL_DIR/plantillas" -name "plantilla-${NN}-*.tex" | head -1)"
[[ -f "$TPL" ]] || die "No se encontró la plantilla $NN en $EVAL_DIR/plantillas/"

DESTDIR="$COURSE/04_EVALUACIONES/$SUB"; mkdir -p "$DESTDIR"
DEST="$DESTDIR/${FECHA}_${SIG}.tex"
[[ -e "$DEST" ]] && die "Ya existe: $DEST (use otra --fecha)"

# Datos para metadatos
CURSO_LABEL="$(basename "$COURSE" | sed -E 's/^course_[0-9]+_//; s/[_-]+/ /g')"
DOC="$(config_get docente)"; DT="$(config_get docente_titulo)"; [[ -n "$DT" ]] && DOC="$DT $DOC"
FECHA_LARGA="$(date -d "$FECHA" '+%d de %B de %Y' 2>/dev/null || echo "$FECHA")"

cp "$TPL" "$DEST"
sed -i -E \
  -e "s|\\\\curso\{[^}]*\}|\\\\curso{${CURSO_LABEL}}|" \
  -e "s|\\\\docente\{[^}]*\}|\\\\docente{${DOC}}|" \
  -e "s|\\\\universidad\{[^}]*\}|\\\\universidad{$(config_get universidad)}|" \
  -e "s|\\\\periodo\{[^}]*\}|\\\\periodo{Semestre $(config_get ciclo)}|" \
  -e "s|\\\\tipoevaluacion\{[^}]*\}|\\\\tipoevaluacion{${TITULO}}|" \
  -e "s|\\\\fechaevaluacion\{[^}]*\}|\\\\fechaevaluacion{${FECHA_LARGA}}|" \
  "$DEST"

ok "Evaluación creada: ${DEST}"
echo "Siguiente:"
echo "  1. Edita las preguntas en $DEST"
echo "  2. Compila:  ./scripts/build-evaluacion.sh \"$DEST\" --modo todos"
echo "     (genera examen, hoja de claves y solucionario)"
