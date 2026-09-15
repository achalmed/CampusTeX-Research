#!/usr/bin/env bash
# ============================================================
# new-session.sh — Crea una sesión en un curso (§4.3, M5)
# ============================================================
# Uso:
#   ./scripts/new-session.sh CURSO NN "TÍTULO" [--tipo clase|laboratorio|taller|evaluacion] [--quarto] [--artefacto NOMBRE]
#
# Ejemplos:
#   ./scripts/new-session.sh econometria-i 07 "Series temporales"                 # clase → deck.tex (Beamer)
#   ./scripts/new-session.sh econometria-i 08 "Panel" --tipo laboratorio          # → cuaderno.ipynb
#   ./scripts/new-session.sh excel 21 "Tablas dinámicas" --tipo taller --artefacto tablas.ods
#
# Crea docencia/cursos/<curso>/03-sesiones/sNN-<slug>/ con sesion.yml, guion.md y el artefacto del tipo
# (clase: deck.tex o deck.qmd con --quarto, con el logo al lado; laboratorio: cuaderno.ipynb; evaluacion:
# evaluacion.tex de academic-exam; taller: el .ods/.xlsx lo creas tú — se declara y el validador lo exige).
# Sin subcarpetas de anatomía: el arco antes/durante/después vive en guion.md.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,17p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$(course_dir "$1")" || die "No es un curso (falta curso.yml): $1"
NUM="$(printf '%02d' "$((10#$2))")"; TITLE="$3"; shift 3
TIPO="clase"; QUARTO=0; ART=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tipo) TIPO="$2"; shift 2 ;;
    --quarto) QUARTO=1; shift ;;
    --artefacto) ART="$2"; shift 2 ;;
    *) usage ;;
  esac
done
case "$TIPO" in clase|laboratorio|taller|evaluacion) : ;; *) die "tipo no admitido: $TIPO" ;; esac
if session_dir "$COURSE" "$NUM" >/dev/null 2>&1; then die "Ya existe la sesión $NUM: $(session_dir "$COURSE" "$NUM")"; fi
SLUG="$(slugify "$TITLE")"; SNAME="s${NUM}-${SLUG}"
DEST="$COURSE/03-sesiones/$SNAME"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"

# artefacto por tipo
if [[ -z "$ART" ]]; then
  case "$TIPO" in
    clase)       ART="deck.qmd"; [[ "$QUARTO" -eq 1 ]] || ART="deck.tex" ;;
    laboratorio) ART="cuaderno.ipynb" ;;
    taller)      ART="taller.ods" ;;
    evaluacion)  ART="evaluacion.tex" ;;
  esac
fi
COURSE_SLUG="$(basename "$COURSE")"
RUTA_SESION="$(ruta_repo "$COURSE")/03-sesiones/$SNAME"
mkdir -p "$DEST"
render() {  # render PLANTILLA DESTINO
  sed -e "s|{{NUMBER}}|$NUM|g" -e "s|{{TITLE}}|$TITLE|g" -e "s|{{SESSION_SLUG}}|$SNAME|g" -e "s|{{SLUG}}|$SLUG|g" \
      -e "s|{{COURSE_SLUG}}|$COURSE_SLUG|g" -e "s|{{COURSE}}|$(course_title "$COURSE")|g" -e "s|{{COURSE_SHORT}}|$(course_title "$COURSE")|g" \
      -e "s|{{SESSION_TYPE}}|$TIPO|g" -e "s|{{ARTIFACT}}|$ART|g" -e "s|{{RUTA_SESION}}|$RUTA_SESION|g" \
      -e "s|{{DATE}}|$(date +%Y-%m-%d)|g" -e "s|{{CYCLE}}|$(config_get ciclo)|g" -e "s|{{TEACHER}}|$(config_get docente)|g" \
      -e "s|{{EMAIL}}|$(config_get email)|g" -e "s|{{INSTITUTION}}|$(config_get institucion)|g" -e "s|{{UNIVERSITY}}|$(config_get universidad)|g" \
      -e "s|{{THEME}}|$(config_get tema_beamer Madrid)|g" -e "s|{{ASPECT}}|$(config_get aspecto 169)|g" \
      -e "s|{{DURATION}}|$(config_get duracion_sesion_min 180)|g" -e "s|{{MODALITY}}|$(config_get modalidad presencial)|g" \
      -e "s|{{LEVEL}}|$(config_get nivel pregrado)|g" "$1" > "$2"
}
render "$SCAFFOLDS_DIR/sesion/sesion.yml" "$DEST/sesion.yml"
render "$SCAFFOLDS_DIR/sesion/guion.md" "$DEST/guion.md"
case "$TIPO" in
  clase)
    if [[ "$ART" == *.qmd ]]; then render "$SCAFFOLDS_DIR/sesion/deck.qmd" "$DEST/$ART"; else render "$SCAFFOLDS_DIR/sesion/deck.tex" "$DEST/$ART"; fi
    LOGO="$FW_DIR/$(config_get logo)"; [[ -f "$LOGO" ]] && cp "$LOGO" "$DEST/cau-logo.png" ;;
  laboratorio)
    case "$ART" in
      *.ipynb) printf '{\n "cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# %s\\n", "\\n", "Sesión %s del curso %s."]}],\n "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},\n "nbformat": 4, "nbformat_minor": 5\n}\n' "$TITLE" "$NUM" "$COURSE_SLUG" > "$DEST/$ART" ;;
      *.do|*.py|*.r|*.R|*.rmd|*.Rmd)
        PRE='#'; [[ "$ART" == *.do ]] && PRE='*'
        printf '%s %s — código de la sesión %s: %s\n' "$PRE" "$RUTA_SESION/$ART" "$NUM" "$TITLE" > "$DEST/$ART" ;;
      *) warn "Artefacto '$ART' no generado automáticamente: créalo (el validador lo exige)" ;;
    esac ;;
  evaluacion)
    TPL="$FW_DIR/templates/exam/examen-desarrollo/examen-desarrollo.tex"; cp "$TPL" "$DEST/$ART"
    sed -i -E -e "s|\\\\curso\{[^}]*\}|\\\\curso{$(course_title "$COURSE")}|" -e "s|\\\\tipoevaluacion\{[^}]*\}|\\\\tipoevaluacion{${TITLE}}|" "$DEST/$ART"
    set_identidad "$DEST/$ART" "evaluación de la sesión ${NUM}: ${TITLE}" ;;
  taller)
    warn "Artefacto '$ART' declarado en sesion.yml: crea el libro de cálculo (el validador lo exige)" ;;
esac
ok "Sesión creada: $DEST  (tipo $TIPO, artefacto $ART)"
echo "Siguiente: edita guion.md y $ART; compila con ./scripts/build-session.sh $COURSE_SLUG $NUM"
