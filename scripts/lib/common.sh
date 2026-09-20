#!/usr/bin/env bash
# ============================================================
# scripts/lib/common.sh — Funciones compartidas del framework
# ============================================================
# Se carga con `source` desde todos los scripts de scripts/. No ejecutar directamente.
#
# Modelo (docs/estandar-docencia.md §1; M5, 2026-09-15):
#   - El framework aloja classes/, styles/, themes/, templates/, scaffolds/, scripts/, config/.
#   - El contenido docente vive en el submódulo docencia/ (repo Academic_Class):
#       docencia/cursos/<slug>/            curso.yml · README.md · 01-diseno … 05-recursos
#       docencia/cursos/<slug>/03-sesiones/sNN-<slug>/   sesion.yml · guion.md · <artefacto>
#       docencia/dictados/<AAAA-ciclo>-<institucion>-<materia>/   dictado.yml · publicacion/ (producto)
#       docencia/_inbox/<origen>/          legado por clasificar (temporal)
#   - registro/ (repo privado hermano, git-ignorado): datos de estudiantes por dictado.
#   - Los helpers aceptan la RUTA del curso/dictado o su SLUG (se resuelve contra docencia/).
# ============================================================

set -euo pipefail

# --- Rutas base ---------------------------------------------
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FW_DIR="$(cd "$LIB_DIR/../.." && pwd)"              # raíz del framework
CONFIG_FILE="$FW_DIR/config/course.yml"            # valores por defecto del docente
SCAFFOLDS_DIR="$FW_DIR/scaffolds"                    # esqueletos mínimos: curso/ sesion/ dictado/
BIBLIOGRAPHY_DIR="$FW_DIR/bibliography"              # archivos .bib
DOCENCIA_DIR="$FW_DIR/docencia"                      # submódulo de contenido (repo Academic_Class)
CURSOS_DIR="$DOCENCIA_DIR/cursos"
DICTADOS_DIR="$DOCENCIA_DIR/dictados"
INBOX_DIR="$DOCENCIA_DIR/_inbox"
REGISTRO_DIR="$FW_DIR/registro"                      # repo privado hermano (nunca con remote público)

# --- Salida con color ---------------------------------------
if [[ -t 1 ]]; then
  C_OK=$'\033[0;32m'; C_WARN=$'\033[0;33m'; C_ERR=$'\033[0;31m'
  C_INFO=$'\033[0;36m'; C_OFF=$'\033[0m'
else
  C_OK=""; C_WARN=""; C_ERR=""; C_INFO=""; C_OFF=""
fi

ok()    { echo "${C_OK}[OK]${C_OFF} $*"; }
info()  { echo "${C_INFO}[..]${C_OFF} $*"; }
warn()  { echo "${C_WARN}[!!]${C_OFF} $*" >&2; }
error() { echo "${C_ERR}[ERROR]${C_OFF} $*" >&2; }
die()   { error "$*"; exit 1; }

# --- YAML plano ----------------------------------------------
# yaml_get ARCHIVO CLAVE [DEFAULT] — lee una clave escalar de primer nivel (clave: valor).
yaml_get() {
  local f="$1" key="$2" default="${3:-}" value
  value="$(grep -E "^${key}:" "$f" 2>/dev/null | head -1 \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^"//; s/"$//; s/^'"'"'//; s/'"'"'$//')" || true
  [[ "$value" == "null" ]] && value=""
  echo "${value:-$default}"
}
# config_get CLAVE [DEFAULT] — lee una clave plana de config/course.yml.
config_get() { yaml_get "$CONFIG_FILE" "$1" "${2:-}"; }

# --- Cursos, sesiones y dictados -----------------------------
# is_course DIR — un curso es una carpeta con curso.yml (§4.2)
is_course()  { [[ -f "$1/curso.yml" ]]; }
# is_dictado DIR — un dictado es una carpeta con dictado.yml (§4.4)
is_dictado() { [[ -f "$1/dictado.yml" ]]; }

# course_dir RUTA|SLUG → ruta absoluta del curso (falla si no existe)
course_dir() {
  local c="$1"
  if [[ -d "$c" ]] && is_course "$c"; then (cd "$c" && pwd); return; fi
  if [[ -d "$CURSOS_DIR/$c" ]] && is_course "$CURSOS_DIR/$c"; then echo "$CURSOS_DIR/$c"; return; fi
  return 1
}
# dictado_dir RUTA|CLAVE → ruta absoluta del dictado
dictado_dir() {
  local d="$1"
  if [[ -d "$d" ]] && is_dictado "$d"; then (cd "$d" && pwd); return; fi
  if [[ -d "$DICTADOS_DIR/$d" ]] && is_dictado "$DICTADOS_DIR/$d"; then echo "$DICTADOS_DIR/$d"; return; fi
  return 1
}

sessions_root() { echo "$1/03-sesiones"; }
# session_dir COURSE NN → ruta de la sesión sNN-* de ese curso
session_dir() {
  local course="$1" num match
  num="$(printf '%02d' "$((10#$2))")"
  match="$(find "$course/03-sesiones" -maxdepth 1 -type d -name "s${num}-*" 2>/dev/null | head -1)"
  [[ -n "$match" ]] || return 1
  echo "$match"
}
# session_num SESSION_DIR → NN (lo da la carpeta sNN-…, §7)
session_num() { basename "$1" | sed -E 's/^s([0-9]{2}).*/\1/'; }
# list_sessions COURSE → carpetas de sesión ordenadas
list_sessions() { find "$1/03-sesiones" -maxdepth 1 -type d -name 's[0-9][0-9]-*' 2>/dev/null | sort; }
# list_courses [DIR] → cursos (carpetas con curso.yml) bajo DIR (por defecto docencia/cursos)
list_courses() { find "${1:-$CURSOS_DIR}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | while read -r c; do is_course "$c" && echo "$c"; done; }
# list_dictados → dictados (carpetas con dictado.yml)
list_dictados() { find "$DICTADOS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | while read -r d; do is_dictado "$d" && echo "$d"; done; }
# session_artifact SESSION_DIR → nombre del artefacto declarado en sesion.yml (vacío si no hay)
session_artifact() { yaml_get "$1/sesion.yml" artefacto; }
# course_title COURSE → título del curso (curso.yml)
course_title() { yaml_get "$1/curso.yml" titulo "$(basename "$1")"; }

# slugify "Texto Con Tildes" → texto-con-tildes (kebab-case ASCII, §4.5)
slugify() {
  echo "$1" \
    | sed 'y/áéíóúüñÁÉÍÓÚÜÑ/aeiouunAEIOUUN/' \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'
}
is_kebab() { [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; }

# --- Identidad de archivo (NORMATIVA_ARCHIVOS §6) ------------
# ruta_repo ARCHIVO → ruta relativa a la raíz del repo git que lo contiene (docencia/ es un repo; el framework, otro)
ruta_repo() {
  local f raiz
  f="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  raiz="$(git -C "$(dirname "$f")" rev-parse --show-toplevel 2>/dev/null || echo "$FW_DIR")"
  echo "${f#"$raiz"/}"
}

# set_identidad ARCHIVO "qué es" — escribe la línea 1 `%% <ruta> — <qué es>` de un .tex copiado desde una plantilla.
set_identidad() {
  local f="$1" que="$2" rel linea
  rel="$(ruta_repo "$f")"
  linea="%% ${rel} — ${que}"
  if head -4 "$f" | grep -qE '^%%? [^ ]+ — '; then
    awk -v L="$linea" 'NR<=4 && !done && /^%%? [^ ]+ — / {print L; done=1; next} {print}' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  elif head -1 "$f" | grep -q '^%!TEX'; then
    sed -i "1a\\
${linea}" "$f"
  else
    sed -i "1i\\
${linea}" "$f"
  fi
}

# --- Compilación LaTeX --------------------------------------
# latex_engine ARCHIVO.tex → motor (LuaLaTeX salvo override explícito `%!TEX program = …`)
latex_engine() {
  local tex="$1" magic
  magic="$(head -5 "$tex" | grep -oiE '%\s*!TEX\s+program\s*=\s*(pdflatex|xelatex|lualatex)' \
    | sed -E 's/.*=\s*//' | tr '[:upper:]' '[:lower:]')" || true
  if [[ -n "$magic" ]]; then echo "$magic"; return; fi
  echo "lualatex"
}

# compile_tex ARCHIVO.tex → compila en el directorio del archivo
compile_tex() {
  local tex="$1" compilador engine dir base
  compilador="$(eval echo "$(config_get compilador)")"
  dir="$(cd "$(dirname "$tex")" && pwd)"
  base="$(basename "$tex")"
  # Los documentos del framework (\documentclass{academic-*}) van SIEMPRE por scripts/build.sh (TEXINPUTS de las capas).
  if grep -qE '\\documentclass(\[[^]]*\])?\{academic-' "$tex"; then
    info "Documento del framework → scripts/build.sh: $base"
    bash "$FW_DIR/scripts/build.sh" "$tex"
    return
  fi
  if [[ -n "$compilador" && -x "$compilador" ]]; then
    info "Compilando con compilador universal: $base"
    "$compilador" -s "$dir/${base%.tex}"
  else
    engine="$(latex_engine "$tex")"
    info "Compilando con $engine (x2): $base"
    ( cd "$dir" \
      && "$engine" -interaction=nonstopmode -halt-on-error "$base" >/dev/null \
      && "$engine" -interaction=nonstopmode -halt-on-error "$base" >/dev/null )
  fi
}

# require_cmd comando → falla con mensaje claro si no existe
require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Se requiere '$1' y no está instalado."
}
