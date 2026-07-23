#!/usr/bin/env bash
# ============================================================
# stats.sh — Resumen de un curso
# ============================================================
# Uso:
#   ./scripts/stats.sh COURSE_DIR
#
# Muestra por sesión: número, título (metadata.yml), decks en
# 02_Clase/, PDFs compilados y nº de actividades (03_Actividad/).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,11p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$1"
is_course "$COURSE" || die "No parece un curso: $COURSE"

meta_get() { grep -E "^$2:" "$1" 2>/dev/null | head -1 \
  | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^"//; s/"$//'; }

printf '%s\n\n' "Curso: $(basename "$COURSE")"
total=0
printf '%-4s %-34s %5s %5s %6s\n' "N°" "TÍTULO" "DECK" "PDF" "ACTIV"
printf '%s\n' "------------------------------------------------------------"
for s in $(list_sessions "$COURSE"); do
  total=$((total + 1))
  meta="$s/metadata.yml"
  num="$(meta_get "$meta" numero)"
  titulo="$(meta_get "$meta" titulo)"
  deck="$(find "$s/02_Clase" \( -name '*.tex' -o -name '*.qmd' \) -not -path '*index_files*' 2>/dev/null | wc -l)"
  pdf="$(find "$s/02_Clase" -name '*.pdf' 2>/dev/null | wc -l)"
  act="$(find "$s/03_Actividad" -type f -not -name '.gitkeep' 2>/dev/null | wc -l)"
  printf '%-4s %-34.34s %5s %5s %6s\n' "${num:-?}" "${titulo:-$(basename "$s")}" "$deck" "$pdf" "$act"
done
echo
echo "Total: $total sesiones"
