#!/usr/bin/env bash
# ============================================================
# build-evaluacion.sh — Compila una evaluación (evaluacion.cls)
# ============================================================
# Uso:
#   ./scripts/build-evaluacion.sh ARCHIVO.tex [--modo MODO] [--clean]
#
# MODO (por defecto: examen):
#   examen      → PDF para el estudiante (oculta soluciones/claves)
#   claves      → hoja de claves objetivas          → ARCHIVO-claves.pdf
#   soluciones  → solucionario completo             → ARCHIVO-soluciones.pdf
#   todos       → genera los tres PDF
#
# El modo se aplica SIN editar el .tex (vía \PassOptionsToClass). Se compila
# dos veces (los totales de puntos y el nº de páginas se calculan por el .aux).
# La clase evaluacion.cls se localiza vía TEXINPUTS (no hace falta copiarla).
#
# Requiere TeX Live con: tcolorbox, tasks, libertinus-type1, fontawesome5.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 1; }

FILE=""; MODO="examen"; CLEAN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --modo) MODO="$2"; shift 2 ;;
    --clean) CLEAN=1; shift ;;
    *) FILE="$1"; shift ;;
  esac
done
[[ -f "$FILE" ]] || die "No existe el archivo: $FILE"
[[ -f "$EVAL_DIR/evaluacion.cls" ]] || die "Falta $EVAL_DIR/evaluacion.cls"

DIR="$(cd "$(dirname "$FILE")" && pwd)"
BASE="$(basename "$FILE" .tex)"
export TEXINPUTS="$EVAL_DIR:${TEXINPUTS:-}"

if [[ "$CLEAN" -eq 1 ]]; then
  ( cd "$DIR" && rm -f "$BASE"*.aux "$BASE"*.log "$BASE"*.out "$BASE"*.toc "$BASE"*.fls "$BASE"*.fdb_latexmk )
  ok "Auxiliares de $BASE eliminados."; exit 0
fi

# compila_modo MODO — compila una variante (dos pasadas) con jobname propio
compila_modo() {
  local modo="$1" opt jobname
  case "$modo" in
    examen)     opt="";                                              jobname="$BASE" ;;
    claves)     opt="\\PassOptionsToClass{claves}{evaluacion}";      jobname="$BASE-claves" ;;
    soluciones) opt="\\PassOptionsToClass{soluciones}{evaluacion}";  jobname="$BASE-soluciones" ;;
    *) die "MODO no válido: $modo (use examen|claves|soluciones|todos)" ;;
  esac
  require_cmd pdflatex
  info "Compilando modo '$modo' → $jobname.pdf (2 pasadas)"
  ( cd "$DIR" \
    && pdflatex -interaction=nonstopmode -halt-on-error -jobname "$jobname" "${opt}\\input{$BASE.tex}" >/dev/null \
    && pdflatex -interaction=nonstopmode -halt-on-error -jobname "$jobname" "${opt}\\input{$BASE.tex}" >/dev/null ) \
    && ok "PDF: $DIR/$jobname.pdf" || { error "Falló la compilación ($modo). Revise $DIR/$jobname.log"; return 1; }
}

if [[ "$MODO" == "todos" ]]; then
  fail=0
  for m in examen claves soluciones; do compila_modo "$m" || fail=1; done
  exit "$fail"
else
  compila_modo "$MODO"
fi
