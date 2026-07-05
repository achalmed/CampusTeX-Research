#!/usr/bin/env bash
# ============================================================
# stats.sh — Estadísticas del curso
# ============================================================
# Uso:
#   ./scripts/stats.sh
#
# Muestra un resumen por sesión: título (de metadata.yml),
# formato, número de fuentes, PDFs compilados y materiales.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

meta_get() { # meta_get ARCHIVO CLAVE
  grep -E "^$2:" "$1" 2>/dev/null | head -1 \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^"//; s/"$//'
}

printf '%s\n' "Curso: $(config_get curso) — $(config_get ciclo)"
printf '%s\n' "Docente: $(config_get docente)"
echo

total=0
printf '%-4s %-38s %-9s %5s %5s %6s\n' "N°" "TÍTULO" "FORMATO" "SRC" "PDF" "PRÁCT"
printf '%s\n' "--------------------------------------------------------------------------"
for dir in $(list_sessions); do
  total=$((total + 1))
  meta="$dir/metadata.yml"
  num="$(meta_get "$meta" numero)"
  titulo="$(meta_get "$meta" titulo)"
  formato="$(meta_get "$meta" formato_slides)"
  # En proyectos Quarto la fuente es el .qmd (el .tex es generado)
  if find "$dir/slides" -maxdepth 1 -name '*.qmd' 2>/dev/null | grep -q .; then
    src="$(find "$dir/slides" -maxdepth 1 -name '*.qmd' | wc -l)"
  else
    src="$(find "$dir/slides" -maxdepth 2 -name '*.tex' 2>/dev/null | wc -l)"
  fi
  pdf="$(find "$dir/slides" -maxdepth 2 -name '*.pdf' 2>/dev/null | wc -l)"
  pract="$(find "$dir/practice" -type f -not -name '.gitkeep' 2>/dev/null | wc -l)"
  printf '%-4s %-38.38s %-9s %5s %5s %6s\n' \
    "${num:-?}" "${titulo:-$(basename "$dir")}" "${formato:-?}" "$src" "$pdf" "$pract"
done
echo
echo "Total: $total sesiones"
