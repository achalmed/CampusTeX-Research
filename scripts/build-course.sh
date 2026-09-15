#!/usr/bin/env bash
# ============================================================
# build-course.sh — Compila un curso completo (M5)
# ============================================================
# Uso:
#   ./scripts/build-course.sh CURSO [--solo-sesiones]     # CURSO: ruta o slug
#
# Compila (1) los .tex de 01-diseno/ y 05-recursos/investigacion/ (omitir con --solo-sesiones)
# y (2) el artefacto de cada sesión (build-session.sh). Continúa aunque algo falle y resume al final.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,10p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$(course_dir "$1")" || die "No es un curso: $1"
SOLO_SESIONES=0
[[ "${2:-}" == "--solo-sesiones" ]] && SOLO_SESIONES=1

declare -a fallos=()
if [[ "$SOLO_SESIONES" -eq 0 ]]; then
  while IFS= read -r -d '' tex; do
    compile_tex "$tex" || fallos+=("$tex")
  done < <(find "$COURSE/01-diseno" "$COURSE/05-recursos/investigacion" -name '*.tex' -not -path '*index_files*' -not -path '*/vendor/*' -print0 2>/dev/null)
fi
while IFS= read -r dir; do
  [[ -n "$dir" ]] || continue
  "$FW_DIR/scripts/build-session.sh" "$COURSE" "$(session_num "$dir")" || fallos+=("sesión $(basename "$dir")")
done < <(list_sessions "$COURSE")
echo
if [[ ${#fallos[@]} -eq 0 ]]; then ok "Curso compilado sin errores."
else error "Fallaron ${#fallos[@]} compilaciones:"; printf '  - %s\n' "${fallos[@]}"; exit 1; fi
