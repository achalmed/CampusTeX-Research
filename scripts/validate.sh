#!/usr/bin/env bash
# ============================================================
# validate.sh — Valida la estructura del framework
# ============================================================
# Uso:
#   ./scripts/validate.sh
#
# Comprueba:
#   - Que exista config/course.yml con las claves mínimas.
#   - Que cada sesión tenga la estructura canónica:
#     metadata.yml, README.md, slides/ con fuente (.tex|.qmd),
#     teaching/, practice/, evaluation/, homework/, resources/.
#   - Que metadata.yml tenga los campos obligatorios.
#
# Devuelve código de salida distinto de 0 si hay errores
# (los avisos [!!] no hacen fallar la validación).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

errors=0
err() { error "$*"; errors=$((errors + 1)); }

# --- Configuración global ------------------------------------
[[ -f "$CONFIG_FILE" ]] || die "Falta config/course.yml"
for key in curso docente institucion ciclo; do
  [[ -n "$(config_get "$key")" ]] || err "config/course.yml: falta la clave '$key'"
done

# --- Sesiones -------------------------------------------------
REQUIRED_DIRS=(slides teaching practice evaluation homework resources)
REQUIRED_META=(numero titulo duracion_minutos formato_slides estado)

for dir in $(list_sessions); do
  name="$(basename "$dir")"
  info "Validando $name"

  [[ -f "$dir/metadata.yml" ]] || { err "$name: falta metadata.yml"; continue; }
  [[ -f "$dir/README.md" ]]    || err "$name: falta README.md"

  for sub in "${REQUIRED_DIRS[@]}"; do
    [[ -d "$dir/$sub" ]] || err "$name: falta el directorio $sub/"
  done

  for key in "${REQUIRED_META[@]}"; do
    grep -qE "^${key}:" "$dir/metadata.yml" || err "$name: metadata.yml sin campo '$key'"
  done

  src_count="$(find "$dir/slides" -maxdepth 2 \( -name '*.tex' -o -name '*.qmd' \) \
    -not -path '*index_files*' 2>/dev/null | wc -l)"
  [[ "$src_count" -gt 0 ]] || err "$name: slides/ sin fuente .tex ni .qmd"

  pdf_count="$(find "$dir/slides" -maxdepth 2 -name '*.pdf' 2>/dev/null | wc -l)"
  [[ "$pdf_count" -gt 0 ]] || warn "$name: sin PDF compilado (ejecuta build-session.sh)"
done

echo
if [[ "$errors" -eq 0 ]]; then
  ok "Estructura válida. Sin errores."
else
  error "Validación con $errors error(es)."
  exit 1
fi
