#!/usr/bin/env bash
# ============================================================
# new-evaluacion.sh — Crea una evaluación en un curso (academic-exam)
# ============================================================
# Uso:
#   ./scripts/new-evaluacion.sh CURSO TIPO "TÍTULO" [--fecha AAAAMMDD]
#
# CURSO: ruta o slug. TIPO (número 01–12 o nombre): examen-desarrollo, examen-objetivo,
#   examen-problemas, practica-calificada, practica-dirigida, laboratorio,
#   control-de-lectura, examen-oral, caso-estudio, tarea, banco-de-preguntas, solucionario.
#
# Copia templates/exam/<tipo>/ a <curso>/04-evaluaciones/<subcarpeta>/AAAAMMDD_sigla.tex y
# rellena metadatos desde curso.yml y config/course.yml. Compilar con build.sh --modo todos.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage

COURSE="$(course_dir "$1")" || die "No es un curso: $1"
TIPO="$2"; TITULO="$3"; FECHA=""
[[ "${4:-}" == "--fecha" ]] && FECHA="$5"
[[ -n "$FECHA" ]] || FECHA="$(date +%Y%m%d)"

# TIPO → (nombre de plantilla · subcarpeta de 04-evaluaciones · sigla)
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
  11|banco-de-preguntas)  NAME=banco-de-preguntas;  SUB=banco;           SIG=BP  ;;
  12|solucionario)        NAME=solucionario;        SUB=soluciones;      SIG=SOL ;;
  *) die "TIPO no reconocido: $TIPO" ;;
esac

TPL="$FW_DIR/templates/exam/$NAME/$NAME.tex"
[[ -f "$TPL" ]] || die "Falta la plantilla $TPL"
DESTDIR="$COURSE/04-evaluaciones/$SUB"; mkdir -p "$DESTDIR"
DEST="$DESTDIR/${FECHA}_${SIG,,}.tex"      # sigla en minúsculas (NORMATIVA_ARCHIVOS §4)
[[ -e "$DEST" ]] && die "Ya existe: $DEST (use otra --fecha)"

CURSO_LABEL="$(course_title "$COURSE")"
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

set_identidad "$DEST" "${NAME//-/ }: ${TITULO}"
ok "Evaluación creada: ${DEST}"
echo "Compila:  ./scripts/build.sh \"$DEST\" --modo todos   (examen · claves · soluciones)"
