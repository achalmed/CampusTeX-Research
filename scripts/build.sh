#!/usr/bin/env bash
# ============================================================
# build.sh — Compila CUALQUIER documento del framework (LuaLaTeX)
# ============================================================
# Uso:
#   ./scripts/build.sh ARCHIVO.tex [--modo MODO] [--clean]
#
# Motor único: LuaLaTeX (dos pasadas; con citas, LuaLaTeX → Biber → LuaLaTeX × 2). Localiza clases, estilos, tema
# Beamer y config vía TEXINPUTS, así el documento solo hace \documentclass{academic-*}. Las citas (APA, Zotero) se
# buscan en la carpeta del documento y en la de la exportación de Zotero (ZOTERO_BIB de core/env.sh), por BIBINPUTS.
#
# --modo (solo evaluaciones, academic-exam): examen | claves | soluciones | todos
#   Aplica la opción de clase SIN editar el .tex (\PassOptionsToClass) y nombra
#   la salida ARCHIVO[-claves|-soluciones].pdf. Sin --modo vale el que declare el
#   documento en sus 30 primeras líneas (% !MODO = soluciones); si no declara, examen.
#   Así F5 de LaTeX Studio y de TeXstudio compila la versión que el documento pide.
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

# Sin --modo, el que declara el documento: «% !MODO = soluciones» en sus 30 primeras líneas
if [[ -z "$MODO" ]]; then
  MODO="$(head -n 30 "$FILE" | sed -nE 's/^[[:space:]]*%[[:space:]]*![[:space:]]*MODO[[:space:]]*=[[:space:]]*([[:alnum:]]+).*/\1/Ip' | head -n 1)"
  MODO="${MODO,,}"
  [[ -n "$MODO" ]] && info "Modo declarado en el documento: $MODO"
fi

# TEXINPUTS: capas del framework (+ evaluaciones/ mientras exista, compat.)
export TEXINPUTS=".:$FW_DIR/classes:$FW_DIR/styles:$FW_DIR/config:$FW_DIR/themes:$FW_DIR/assets:${TEXINPUTS:-}"

# BIBINPUTS: la carpeta del documento (su referencias.bib) y la de la exportación automática de Zotero (zotero.bib)
if [[ -z "${ZOTERO_BIB:-}" && -f "$FW_DIR/../core/env.sh" ]]; then
  ZOTERO_BIB="$(bash -c 'source "$1" && printf "%s" "$ZOTERO_BIB"' _ "$FW_DIR/../core/env.sh" 2>/dev/null)" || ZOTERO_BIB=""
fi
export BIBINPUTS=".:${ZOTERO_BIB:+$(dirname "$ZOTERO_BIB")}:$FW_DIR/bibliography:${BIBINPUTS:-}"

if [[ "$CLEAN" -eq 1 ]]; then
  ( cd "$DIR" && rm -f "$BASE"*.aux "$BASE"*.log "$BASE"*.out "$BASE"*.toc \
      "$BASE"*.nav "$BASE"*.snm "$BASE"*.vrb "$BASE"*.fls "$BASE"*.fdb_latexmk \
      "$BASE"*.bcf "$BASE"*.bbl "$BASE"*.blg "$BASE"*.run.xml "$BASE"*.synctex.gz )
  ok "Auxiliares de $BASE eliminados."; exit 0
fi

require_cmd "$ENGINE"

# compila JOBNAME PREAMBULO — LuaLaTeX; si el documento cita (hay citas en el .bcf), Biber y dos pasadas más
compila() {
  local jobname="$1" pre="$2"
  # -synctex=1: saltar entre el PDF y el código (LaTeX Studio, TeXstudio, Okular)
  pasada() { "$ENGINE" -synctex=1 -interaction=nonstopmode -halt-on-error -jobname "$jobname" "${pre}\\input{$BASE.tex}" >/dev/null 2>&1; }
  ( cd "$DIR" && pasada \
    && if [[ -f "$jobname.bcf" ]] && grep -q "<bcf:citekey" "$jobname.bcf"; then
         biber --quiet "$jobname" >/dev/null 2>&1 || { echo "Biber falló: revise $DIR/$jobname.blg" >&2; exit 1; }
         pasada
       fi \
    && pasada ) \
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
  examen|"")  compila "$BASE" "" ;;
  *)          die "MODO no válido: $MODO (examen|claves|soluciones|todos)" ;;
esac
