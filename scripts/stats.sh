#!/usr/bin/env bash
# ============================================================
# stats.sh — Resumen de un curso por sesión (M5, 2026-09-15)
# ============================================================
# Uso:
#   ./scripts/stats.sh CURSO        # ruta o slug (docencia/cursos/<slug>)
#
# Por sesión: número (carpeta sNN), título, tipo y estado (sesion.yml),
# artefacto declarado (✓ existe / ✗ falta), PDF en la sesión y estado del guion.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,10p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$(course_dir "$1")" || die "No es un curso (falta curso.yml): $1"

printf '%s — %s (%s, %s)\n\n' "$(basename "$COURSE")" "$(course_title "$COURSE")" "$(yaml_get "$COURSE/curso.yml" tipo)" "$(yaml_get "$COURSE/curso.yml" estado)"
total=0
printf '%-3s %-32s %-11s %-8s %-4s %-24s %4s %-8s\n' "N°" "TÍTULO" "TIPO" "ESTADO" "ART" "ARTEFACTO" "PDF" "GUION"
printf '%s\n' "----------------------------------------------------------------------------------------------------"
while IFS= read -r s; do [[ -n "$s" ]] || continue
  total=$((total + 1)); sy="$s/sesion.yml"
  art="$(session_artifact "$s")"
  [[ -n "$art" && -f "$s/$art" ]] && marca="✓" || marca="✗"
  pdf="$(find "$s" -maxdepth 1 -name '*.pdf' 2>/dev/null | wc -l)"
  guion="$([[ -f "$s/guion.md" ]] && yaml_get "$s/guion.md" estado "?" || echo "falta")"
  printf '%-3s %-32.32s %-11.11s %-8.8s %-4s %-24.24s %4s %-8s\n' "$(session_num "$s")" "$(yaml_get "$sy" titulo "$(basename "$s")")" \
    "$(yaml_get "$sy" tipo "?")" "$(yaml_get "$sy" estado "?")" "$marca" "${art:-—}" "$pdf" "$guion"
done < <(list_sessions "$COURSE")
echo
echo "Total: $total sesiones · unidades en curso.yml: $(grep -cE '^- id:' "$COURSE/curso.yml" 2>/dev/null || echo 0)"
