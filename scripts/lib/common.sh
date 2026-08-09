#!/usr/bin/env bash
# ============================================================
# scripts/lib/common.sh — Funciones compartidas del framework
# ============================================================
# Se carga con `source` desde todos los scripts de scripts/.
# No ejecutar directamente.
#
# Modelo (ver ../README.md):
#   - El framework aloja scaffolds/, libraries/, classes/, styles/, themes/, templates/.
#   - Los cursos viven FUERA, en ~/Documents/Academic_Class-*/course_NN_*/,
#     con estructura 00–09 y sesiones 03_SESIONES/SNN_slug/ (02_Clase/…).
#   - Por eso los helpers de curso/sesión reciben la RUTA del curso.
# ============================================================

set -euo pipefail

# --- Rutas base ---------------------------------------------
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FW_DIR="$(cd "$LIB_DIR/../.." && pwd)"              # raíz del framework
CONFIG_FILE="$FW_DIR/config/course.yml"            # valores por defecto del docente
SCAFFOLDS_DIR="$FW_DIR/scaffolds"                    # esqueletos de carpetas (course/session/period)
LIBRARIES_DIR="$FW_DIR/libraries"                    # bancos reutilizables
BIBLIOGRAPHY_DIR="$FW_DIR/bibliography"              # archivos .bib

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

# --- Configuración (valores por defecto) --------------------
# config_get CLAVE [DEFAULT] — lee una clave plana de config/course.yml.
config_get() {
  local key="$1" default="${2:-}" value
  value="$(grep -E "^${key}:" "$CONFIG_FILE" 2>/dev/null | head -1 \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^"//; s/"$//')" || true
  echo "${value:-$default}"
}

# --- Cursos y sesiones (reciben la RUTA del curso) ----------
# is_course DIR — ¿DIR tiene pinta de curso 00–09?
is_course() { [[ -d "$1/00_ADMINISTRACION" && -d "$1/03_SESIONES" ]]; }

# sessions_root COURSE → ruta de 03_SESIONES
sessions_root() { echo "$1/03_SESIONES"; }

# session_dir COURSE NN → ruta de la sesión SNN_* de ese curso
session_dir() {
  local course="$1" num match
  num="$(printf '%02d' "$((10#$2))")"
  match="$(find "$course/03_SESIONES" -maxdepth 1 -type d -name "S${num}_*" 2>/dev/null | head -1)"
  [[ -n "$match" ]] || return 1
  echo "$match"
}

# list_sessions COURSE → carpetas de sesión ordenadas
list_sessions() { find "$1/03_SESIONES" -maxdepth 1 -type d -name 'S[0-9]*' 2>/dev/null | sort; }

# list_courses ACADEMIC_CLASS → carpetas de curso ordenadas
list_courses() { find "$1" -maxdepth 1 -type d -name 'course_*' 2>/dev/null | sort; }

# slugify "Texto Con Tildes" → texto_con_tildes
slugify() {
  echo "$1" \
    | sed 'y/áéíóúüñÁÉÍÓÚÜÑ/aeiouunAEIOUUN/' \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g'
}

# --- Compilación LaTeX --------------------------------------
# latex_engine ARCHIVO.tex → motor a usar.
#   El framework es LuaLaTeX-only (migración 2026). Se honra un override
#   explícito `%!TEX program = pdflatex|xelatex|lualatex` (para documentos
#   legacy que lo declaren) y, en su defecto, se usa lualatex. Se retiró la
#   antigua heurística `fontspec → xelatex`: bajo LuaLaTeX fontspec es el
#   caso nativo, y además fallaba con los documentos del framework (que solo
#   hacen \documentclass{academic-*}, sin la cadena "fontspec" en el propio
#   .tex, y caían por error a pdflatex).
latex_engine() {
  local tex="$1" magic
  magic="$(head -5 "$tex" | grep -oiE '%\s*!TEX\s+program\s*=\s*(pdflatex|xelatex|lualatex)' \
    | sed -E 's/.*=\s*//' | tr '[:upper:]' '[:lower:]')" || true
  if [[ -n "$magic" ]]; then echo "$magic"; return; fi
  echo "lualatex"   # motor por defecto del framework (LuaLaTeX-only)
}

# compile_tex ARCHIVO.tex → compila en el directorio del archivo
compile_tex() {
  local tex="$1" compilador engine dir base
  compilador="$(eval echo "$(config_get compilador)")"
  dir="$(cd "$(dirname "$tex")" && pwd)"
  base="$(basename "$tex")"
  # Los documentos del framework (\documentclass{academic-*}) exigen LuaLaTeX
  # + TEXINPUTS de las capas del framework; el compilador universal no resuelve
  # las clases academic-* ni respeta %!TEX (auditoría A1). Van SIEMPRE por
  # scripts/build.sh, que es quien define ese entorno.
  if grep -qE '\\documentclass(\[[^]]*\])?\{academic-' "$tex"; then
    info "Documento del framework → scripts/build.sh: $base"
    bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/build.sh" "$tex"
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
