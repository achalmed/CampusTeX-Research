#!/usr/bin/env bash
# ============================================================
# build.sh — Compila CUALQUIER documento del framework (LuaLaTeX)
# ============================================================
# Uso:
#   ./scripts/build.sh ARCHIVO.tex [--modo MODO] [--clean]
#
# Motor único: LuaLaTeX (dos pasadas). Localiza clases, estilos, tema Beamer y
# config vía TEXINPUTS, así el documento solo hace \documentclass{academic-*}.
#
# --modo (solo evaluaciones, academic-exam): examen | claves | soluciones | todos
#   Aplica la opción de clase SIN editar el .tex (\PassOptionsToClass) y nombra
#   la salida ARCHIVO[-claves|-soluciones].pdf.
# --clean : elimina auxiliares del documento.
#
# Reemplaza a build-session/build-course/build-evaluacion (todo es LuaLaTeX ahora).
# ============================================================

# Motor LaTeX (punto de conmutación único; LuaLaTeX es el soportado).
ENGINE="${ENGINE:-lualatex}"

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 1; }

FILE=""; MODO=""; CLEAN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --modo) MODO="$2"; shift 2 ;;
    --clean) CLEAN=1; shift ;;
    *) FILE="$1"; shift ;;
  esac
done
[[ -f "$FILE" ]] || die "No existe el archivo: $FILE"

DIR="$(cd "$(dirname "$FILE")" && pwd)"
BASE="$(basename "$FILE" .tex)"

# TEXINPUTS: capas del framework (+ evaluaciones/ mientras exista, compat.)
export TEXINPUTS=".:$FW_DIR/classes:$FW_DIR/styles:$FW_DIR/config:$FW_DIR/themes:$FW_DIR/assets:${TEXINPUTS:-}"

if [[ "$CLEAN" -eq 1 ]]; then
  ( cd "$DIR" && rm -f "$BASE"*.aux "$BASE"*.log "$BASE"*.out "$BASE"*.toc \
      "$BASE"*.nav "$BASE"*.snm "$BASE"*.vrb "$BASE"*.fls "$BASE"*.fdb_latexmk )
  ok "Auxiliares de $BASE eliminados."; exit 0
fi

require_cmd "$ENGINE"

# compila JOBNAME PREAMBULO — dos pasadas LuaLaTeX
compila() {
  local jobname="$1" pre="$2"
  ( cd "$DIR" \
    && "$ENGINE" -interaction=nonstopmode -halt-on-error -jobname "$jobname" "${pre}\\input{$BASE.tex}" >/dev/null 2>&1 \
    && "$ENGINE" -interaction=nonstopmode -halt-on-error -jobname "$jobname" "${pre}\\input{$BASE.tex}" >/dev/null 2>&1 ) \
    && ok "PDF: $DIR/$jobname.pdf" || { error "Falló: $jobname. Revise $DIR/$jobname.log"; return 1; }
}

modo_pre() { case "$1" in
  examen|"") echo "" ;;
  claves)     echo "\\PassOptionsToClass{claves}{academic-exam}" ;;
  soluciones) echo "\\PassOptionsToClass{soluciones}{academic-exam}" ;;
  *) die "MODO no válido: $1 (examen|claves|soluciones|todos)" ;;
esac; }

case "$MODO" in
  todos)
    fail=0
    compila "$BASE" ""                                        || fail=1
    compila "$BASE-claves" "$(modo_pre claves)"               || fail=1
    compila "$BASE-soluciones" "$(modo_pre soluciones)"       || fail=1
    exit "$fail" ;;
  claves)     info "Modo claves";     compila "$BASE-claves" "$(modo_pre claves)" ;;
  soluciones) info "Modo soluciones"; compila "$BASE-soluciones" "$(modo_pre soluciones)" ;;
  *)          compila "$BASE" "" ;;
esac
