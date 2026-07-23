#!/usr/bin/env bash
# ============================================================
# scripts/lib/common.sh — Funciones compartidas del framework
# ============================================================
# Se carga con `source` desde todos los scripts de scripts/.
# No ejecutar directamente.
#
# Modelo (ver ../README.md):
#   - El framework aloja _PLANTILLAS/ y _BIBLIOTECA/ (compartido).
#   - Los cursos viven FUERA, en ~/Documents/Academic_Class-*/course_NN_*/,
#     con estructura 00–11 y sesiones 03_SESIONES/SNN_slug/ (02_Clase/…).
#   - Por eso los helpers de curso/sesión reciben la RUTA del curso.
# ============================================================

set -euo pipefail

# --- Rutas base ---------------------------------------------
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FW_DIR="$(cd "$LIB_DIR/../.." && pwd)"              # raíz del framework
CONFIG_FILE="$FW_DIR/config/course.yml"            # valores por defecto del docente
PLANTILLAS_DIR="$FW_DIR/_PLANTILLAS"
BIBLIOTECA_DIR="$FW_DIR/_BIBLIOTECA"
EVAL_DIR="$FW_DIR/evaluaciones"                    # sistema LaTeX de evaluaciones (evaluacion.cls)

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
# is_course DIR — ¿DIR tiene pinta de curso 00–11?
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
# latex_engine ARCHIVO.tex → pdflatex | xelatex | lualatex
latex_engine() {
  local tex="$1" magic
  magic="$(head -5 "$tex" | grep -oiE '%\s*!TEX\s+program\s*=\s*(pdflatex|xelatex|lualatex)' \
    | sed -E 's/.*=\s*//' | tr '[:upper:]' '[:lower:]')" || true
  if [[ -n "$magic" ]]; then echo "$magic"; return; fi
  if grep -qE '\\documentclass.*\{yaac-luatex\}' "$tex"; then echo "lualatex"; return; fi
  if grep -qE '\\documentclass.*\{yaac-xelatex\}' "$tex"; then echo "xelatex"; return; fi
  if grep -q 'fontspec' "$tex"; then echo "xelatex"; return; fi
  echo "pdflatex"
}

# compile_tex ARCHIVO.tex → compila en el directorio del archivo
compile_tex() {
  local tex="$1" compilador engine dir base
  compilador="$(eval echo "$(config_get compilador)")"
  dir="$(cd "$(dirname "$tex")" && pwd)"
  base="$(basename "$tex")"
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
