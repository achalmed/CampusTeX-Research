#!/usr/bin/env bash
# ============================================================
# new-evaluacion.sh — Crea una evaluación en un curso (academic-exam)
# ============================================================
# Uso:
#   ./scripts/new-evaluacion.sh COURSE_DIR TIPO "TÍTULO" [--fecha AAAAMMDD]
#
# TIPO (número 01–12 o nombre): examen-desarrollo, examen-objetivo,
#   examen-problemas, practica-calificada, practica-dirigida, laboratorio,
#   control-de-lectura, examen-oral, caso-estudio, tarea, banco-de-preguntas,
#   solucionario.
#
# Copia templates/exam/<tipo>/ a <curso>/04_EVALUACIONES/<subcarpeta>/AAAAMMDD_SIGLA.tex,
# rellena metadatos desde config/course.yml. Compilar con build.sh --modo todos.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,18p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage

COURSE="$1"; TIPO="$2"; TITULO="$3"; FECHA=""
[[ "${4:-}" == "--fecha" ]] && FECHA="$5"
[[ -n "$FECHA" ]] || FECHA="$(date +%Y%m%d)"
is_course "$COURSE" || die "No parece un curso: $COURSE"

# TIPO → (nombre de plantilla · subcarpeta de 04_EVALUACIONES · sigla)
case "$TIPO" in
  01|examen-desarrollo)   NAME=examen-desarrollo;   SUB=examen_parcial;  SIG=EP  ;;
  02|examen-objetivo)     NAME=examen-objetivo;     SUB=examen_parcial;  SIG=EP  ;;
  03|examen-problemas)    NAME=examen-problemas;    SUB=examen_parcial;  SIG=EP  ;;
  04|practica-calificada) NAME=practica-calificada; SUB=practicas;       SIG=PC  ;;
  05|practica-dirigida)   NAME=practica-dirigida;   SUB=practicas;       SIG=PD  ;;
  06|laboratorio)         NAME=laboratorio;         SUB=laboratorios;    SIG=LAB ;;
  07|control-de-lectura)  NAME=control-de-lectura;  SUB=tareas;          SIG=CL  ;;
  08|examen-oral)         NAME=examen-oral;         SUB=examen_final;    SIG=EO  ;;
  09|caso-estudio)        NAME=caso-estudio;        SUB=proyectos;       SIG=CASO;;
  10|tarea)               NAME=tarea;               SUB=tareas;          SIG=TAR ;;
  11|banco-de-preguntas)  NAME=banco-de-preguntas;  SUB=banco_preguntas; SIG=BP  ;;
  12|solucionario)        NAME=solucionario;        SUB=soluciones;      SIG=SOL ;;
  *) die "TIPO no reconocido: $TIPO" ;;
esac

TPL="$FW_DIR/templates/exam/$NAME/$NAME.tex"
[[ -f "$TPL" ]] || die "Falta la plantilla $TPL"
DESTDIR="$COURSE/04_EVALUACIONES/$SUB"; mkdir -p "$DESTDIR"
DEST="$DESTDIR/${FECHA}_${SIG}.tex"
[[ -e "$DEST" ]] && die "Ya existe: $DEST (use otra --fecha)"

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
echo "Compila:  ./scripts/build.sh \"$DEST\" --modo todos   (examen · claves · soluciones)"
